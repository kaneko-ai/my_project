# nlp/vector_chroma.py

import chromadb
from chromadb.config import Settings
from nlp.embedding_model import embed_text

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_store"))
collection = client.get_or_create_collection(name="articles")

def add_to_chroma(doc_id: str, content: str, metadata: dict):
    embedding = embed_text(content)
    collection.add(
        documents=[content],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[metadata]
    )

def search_chroma(query: str, top_k: int = 5):
    query_vec = embed_text(query)
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)
    hits = []
    for doc, meta, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        hits.append({
            "title": meta.get("title", "No Title"),
            "content": doc,
            "score": round(1 - score, 4),  # 1に近いほど類似
            "metadata": meta
        })
    return hits
