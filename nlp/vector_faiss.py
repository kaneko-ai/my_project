# nlp/vector_faiss.py

import faiss
import numpy as np
from nlp.embedding_model import embed_text

# FAISSインデックス（グローバルで保持）
faiss_index = faiss.IndexFlatL2(384)  # all-MiniLM-L6-v2 の出力サイズ
doc_store = []

def add_to_faiss(doc_id: str, content: str, metadata: dict):
    embedding = embed_text(content)
    faiss_index.add(np.array([embedding]).astype('float32'))
    doc_store.append({
        "id": doc_id,
        "content": content,
        "metadata": metadata
    })

def search_faiss(query: str, top_k: int = 5):
    query_vec = np.array([embed_text(query)]).astype('float32')
    distances, indices = faiss_index.search(query_vec, top_k)
    hits = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(doc_store):
            item = doc_store[idx]
            hits.append({
                "title": item["metadata"].get("title", "No Title"),
                "content": item["content"],
                "score": round(1 / (1 + dist), 4),  # 小さい距離を類似度スコア化
                "metadata": item["metadata"]
            })
    return hits
