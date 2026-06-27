from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import chromadb

from chunker import split_text_into_sentences
from llm_service import generate_rag_answer, rewrite_query_with_history

app = FastAPI(
    title="DocuSearch Modular Conversational RAG Engine",
    description="Stateful microservice supporting query-rewriting and page-level metadata citations."
)

DB_DIR = "./chroma_storage"
chroma_client = chromadb.PersistentClient(path=DB_DIR)
collection = chroma_client.get_or_create_collection(
    name="campus_knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

# Global In-Memory Sessions Storage dictionary mapping session_id -> list of chat messages
SESSION_REGISTRY: Dict[str, List[Dict[str, str]]] = {}

# Structured structural schemas to map page-level inputs safely
class PagePayload(BaseModel):
    page_number: int
    text: str

class DocumentIngest(BaseModel):
    id: str  
    category: str
    pages: List[PagePayload] # Accepts explicit structural list breakdowns

class SearchQuery(BaseModel):
    query: str
    max_results: int = 3

class RAGQuery(BaseModel):
    question: str
    session_id: str = Field(default="default_session")

@app.post("/ingest", status_code=201)
async def ingest_document(doc: DocumentIngest):
    try:
        documents_to_add = []
        metadatas_to_add = []
        ids_to_add = []
        global_chunk_counter = 0
        
        # Track page arrays separately to preserve chronological order indices
        for page_data in doc.pages:
            text_chunks = split_text_into_sentences(page_data.text)
            
            for index, chunk_text in enumerate(text_chunks):
                documents_to_add.append(chunk_text)
                metadatas_to_add.append({
                    "category": doc.category,
                    "parent_id": doc.id,
                    "page_number": page_data.page_number, # Lock structural source page mapping
                    "chunk_index": global_chunk_counter
                })
                ids_to_add.append(f"{doc.id}_p{page_data.page_number}_s{index}")
                global_chunk_counter += 1
                
        if documents_to_add:
            collection.upsert(
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )
        
        return {
            "status": "success",
            "message": f"Document '{doc.id}' cataloged across {len(doc.pages)} pages.",
            "total_sentences_indexed": len(documents_to_add)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def semantic_search(search: SearchQuery):
    try:
        if collection.count() == 0:
            return {"query": search.query, "results": [], "message": "Index is empty."}
            
        raw_results = collection.query(
            query_texts=[search.query],
            n_results=search.max_results
        )
        
        formatted_results = []
        if raw_results.get('ids') and len(raw_results['ids'][0]) > 0:
            for i in range(len(raw_results['ids'][0])):
                formatted_results.append({
                    "chunk_id": raw_results['ids'][0][i],
                    "text": raw_results['documents'][0][i],
                    "category": raw_results['metadatas'][0][i]['category'],
                    "parent_doc_id": raw_results['metadatas'][0][i]['parent_id'],
                    "page_number": raw_results['metadatas'][0][i].get('page_number', 1),
                    "distance": round(raw_results['distances'][0][i], 4)
                })
                
        return {
            "query": search.query,
            "total_matches_returned": len(formatted_results),
            "results": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_knowledge_base(payload: RAGQuery):
    try:
        if collection.count() == 0:
            return {"answer": "The database index is currently empty. Please ingest data first."}
            
        # 1. Fetch or initialize stateful historical context
        chat_history = SESSION_REGISTRY.get(payload.session_id, [])
        
        # 2. Rewrite the user question into a standalone query if history exists
        search_query = rewrite_query_with_history(payload.question, chat_history)
        
        # 3. Perform vector lookup using the rewritten high-purity query
        raw_results = collection.query(
            query_texts=[search_query],
            n_results=1
        )
        
        if not raw_results.get('documents') or len(raw_results['documents'][0]) == 0:
            return {"answer": "No matches found within the localized vector schema."}
            
        retrieved_fact = raw_results['documents'][0][0]
        distance = raw_results['distances'][0][0]
        metadata = raw_results['metadatas'][0][0]
        
        if distance > 1.2:
            return {"answer": "I do not have access to any relevant information to answer that query safely."}

        # 4. Parent Context Window Expansion Strategy
        parent_doc_id = metadata["parent_id"]
        current_index = metadata["chunk_index"]
        
        doc_elements = collection.get(
            where={"parent_id": parent_doc_id}
        )
        
        sorted_chunks = sorted(
            zip(doc_elements['metadatas'], doc_elements['documents']),
            key=lambda x: x[0]['chunk_index']
        )
        
        expanded_context_list = []
        for meta, text in sorted_chunks:
            if current_index <= meta['chunk_index'] <= (current_index + 1):
                expanded_context_list.append(text)
                
        full_expanded_context = " ".join(expanded_context_list)

        # 5. Generate Response using the parent context window
        ai_answer = generate_rag_answer(payload.question, full_expanded_context)
        
        # 6. Commit the current structural exchange to the session state log
        chat_history.append({"role": "user", "content": payload.question})
        chat_history.append({"role": "model", "content": ai_answer})
        SESSION_REGISTRY[payload.session_id] = chat_history
        
        return {
            "question": payload.question,
            "rewritten_query": search_query,
            "local_retrieved_fact": retrieved_fact,
            "distance_score": round(distance, 4),
            "gemini_generated_answer": ai_answer,
            "source_document": parent_doc_id,
            "source_page": metadata.get("page_number", 1) # Return data to frontend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))