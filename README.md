# DocuSearch: Conversational RAG Engine

DocuSearch is an AI-powered document search assistant. It uses a Retrieval-Augmented Generation (RAG) pipeline to read uploaded documents (like PDFs or text files), search through them based on the actual meaning of your question, and generate accurate answers using the Gemini LLM.

Every answer comes with a precise page citation, so you know exactly where the information came from.

---

## How the Pipeline Works

1. Document Ingestion (FastAPI Backend): When you upload a document, the system splits the text into clean sentence blocks.
2. Vector Database Storage (ChromaDB): These sentences are converted into mathematical vectors and stored in a persistent local database (ChromaDB). This allows the system to perform smart semantic searches based on concepts rather than just matching raw keywords.
3. Conversational Query Rewriting: If you ask a vague follow-up question, the engine looks at your previous chat history and automatically rephrases your prompt into a full standalone query before searching the database.
4. Context Synthesis (Gemini LLM): The system retrieves the most relevant sentences along with their surrounding context window and passes them to the Gemini Pro API to generate a natural, verified response.
5. UI Analytics Dashboard (Streamlit): A clean, dark-themed user interface displays your conversational history stack, source tracking badges, and real-time pipeline confidence metrics.

---

## Repository File Structure

* app.py – The Streamlit frontend web dashboard.
* main.py – The FastAPI backend service that manages the database and LLM queries.
* chunker.py – A utility module that cleanly handles sentence-level text splitting.
* llm_service.py – Connects to Gemini for query rewriting and answer generation.
* requirements.txt – List of mandatory Python packages needed to run the application.
* .gitignore – Tells Git to ignore private credential files (.env) and local database folders (chroma_storage).

---

## Getting Started

### 1. Clone the Project
Command: git clone https://github.com/SinghAniket24/docusearch-rag-engine.git
Command: cd docusearch-rag-engine

### 2. Install Dependencies
Command: pip install -r requirements.txt

### 3. Add Your API Key
Create a file named .env in the root folder and add your Gemini API key:
Line to add: GEMINI_API_KEY=your_actual_api_key_here

### 4. Run the Application
Open two separate terminal windows to boot up the microservices:

* Terminal 1 (Start Backend Server): uvicorn main:app --reload
* Terminal 2 (Start Frontend Interface): streamlit run app.py

---

## Testing the Application

1. Open the Streamlit dashboard in your browser.
2. Go to the sidebar on the left, enter a Document ID (e.g., sec_ops_2026), choose a category tag, and upload a multi-page PDF or text file.
3. Click Index Document. Once successful, you will see a validation message confirming how many sentence blocks were indexed.
4. Type a question in the Ask the Engine chat bar (e.g., "What is the policy for critical security patches?").
5. Review the generated response alongside its live Match Quality metrics and the exact Source and Page Citation badge.