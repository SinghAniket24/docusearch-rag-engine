import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    ai_client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")

def generate_rag_answer(question: str, retrieved_fact: str) -> str:
    """
    Sends the retrieved local database fact to the Gemini Cloud 
    and returns a clean response that strictly preserves all conditions.
    """
    system_instructions = (
        f"You are a precise technical assistant. Answer the user prompt using ONLY the provided text fact. "
        f"Be conversational but direct. Do not explicitly say 'according to the text' or 'the fact states'.\n"
        f"CRITICAL CONSTRAINT: You must preserve all specific conditions, requirements, dates, metrics, "
        f"or tenure constraints mentioned in the fact. Do not truncate or omit the rules.\n"
        f"Retrieved Fact: {retrieved_fact}"
    )

    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config={'system_instruction': system_instructions}
    )
    
    return response.text.strip()

def rewrite_query_with_history(question: str, chat_history: list) -> str:
    """
    Analyzes historical conversational context and rephrases vague follow-up 
    queries into a high-purity standalone search question for the vector DB.
    """
    if not chat_history:
        return question

    # Format the recent history for the LLM context block
    history_context = ""
    for turn in chat_history[-4:]:  # Look at the last 2 exchanges (4 turns total)
        history_context += f"{turn['role'].upper()}: {turn['content']}\n"

    system_instructions = (
        "You are an advanced query-rewriting utility. Analyze the conversation history "
        "and the latest user follow-up question. Rephrase the latest question into a "
        "completely independent, standalone search query that contains all necessary "
        "nouns and context. Do not answer the question; only return the rewritten query text."
    )

    prompt = f"Chat History:\n{history_context}\nLatest Question: {question}\nStandalone Query:"

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'system_instruction': system_instructions}
        )
        return response.text.strip()
    except Exception:
        return question  # Fallback to the raw question if any exception occurs