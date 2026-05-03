"""
backend/pipeline.py
Orchestrates the full RAG pipeline: retrieve → prompt → generate.
"""

from langchain_community.vectorstores import FAISS

from backend.retriever import retrieve_relevant_docs
from llm.gemini_api import call_gemini
from llm.prompts import build_prompt


def run_rag_pipeline(query: str, vector_store: FAISS, api_key: str) -> str:
    """
    Full pipeline:
    1. Retrieve the top-5 relevant legal sections.
    2. Build a structured prompt.
    3. Call Gemini and return the answer.
    """
    relevant_docs = retrieve_relevant_docs(query, vector_store, k=5)

    context_parts = []
    for i, doc in enumerate(relevant_docs, 1):
        meta = doc.metadata
        header = f"[{i}] {meta.get('title', 'Legal Section')} ({meta.get('section_number', '')})"
        context_parts.append(f"{header}\n{doc.page_content}")

    context = "\n\n---\n\n".join(context_parts)
    prompt = build_prompt(query, context)

    answer = call_gemini(prompt, api_key)
    return answer
