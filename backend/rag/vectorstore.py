"""
FAISS vector store creation and in-memory caching.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from rag.loader import load_documents

# In-memory cache: domain -> FAISS vector store
_store_cache: dict[str, FAISS] = {}


def get_vectorstore(domain: str) -> FAISS:
    """
    Return the FAISS vector store for a domain.
    Creates and caches it on first access.
    """
    if domain not in _store_cache:
        docs = load_documents(domain)
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
        )
        store = FAISS.from_documents(docs, embeddings)
        _store_cache[domain] = store
    return _store_cache[domain]


def get_retriever(domain: str):
    """Return a retriever from the cached vector store."""
    store = get_vectorstore(domain)
    return store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
