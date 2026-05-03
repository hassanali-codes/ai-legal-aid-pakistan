import os
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "faiss_index")

def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def build_vector_store(chunks: List[Dict], api_key: str) -> FAISS:
    docs = [
        Document(
            page_content=chunk["text"],
            metadata={
                "title": chunk.get("title", ""),
                "category": chunk.get("category", ""),
                "section_number": chunk.get("section_number", ""),
            },
        )
        for chunk in chunks
    ]
    embeddings = _get_embeddings()
    return FAISS.from_documents(docs, embeddings)

def save_vector_store(vector_store: FAISS) -> None:
    os.makedirs(INDEX_DIR, exist_ok=True)
    vector_store.save_local(INDEX_DIR)

def load_vector_store(api_key: str) -> FAISS:
    if not os.path.exists(INDEX_DIR):
        raise FileNotFoundError(f"No saved index found at {INDEX_DIR}")
    embeddings = _get_embeddings()
    return FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )