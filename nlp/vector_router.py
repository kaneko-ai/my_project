# nlp/vector_router.py

from nlp.vector_faiss import add_to_faiss, search_faiss
from nlp.vector_chroma import add_to_chroma, search_chroma

def add_document(doc_id: str, content: str, metadata: dict, backend="chroma"):
    if backend == "chroma":
        add_to_chroma(doc_id, content, metadata)
    elif backend == "faiss":
        add_to_faiss(doc_id, content, metadata)
    else:
        raise ValueError(f"Unsupported backend: {backend}")

def search_vector(query: str, top_k: int = 5, backend="chroma"):
    if backend == "chroma":
        return search_chroma(query, top_k)
    elif backend == "faiss":
        return search_faiss(query, top_k)
    else:
        raise ValueError(f"Unsupported backend: {backend}")
