"""
backend/retriever.py
Performs semantic search over the FAISS vector store.
"""

from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def retrieve_relevant_docs(
    query: str,
    vector_store: FAISS,
    k: int = 5,
) -> List[Document]:
    """Return the top-k most relevant documents for the given query."""
    results = vector_store.similarity_search(query, k=k)
    return results
