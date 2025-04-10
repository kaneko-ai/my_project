# nlp/vector_db.py

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from nlp.embedding_model import embed_text

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_store"))

# コレクション（論文データベース）
collection = client.get_or_create_collection(name="articles")

def add_document(doc_id: str, content: str, metadata: dict):
    """
    要約をChromaに追加
    """
    embedding = embed_text(content)
    collection.add(
        documents=[content],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[metadata]
    )

def search_similar(query: str, top_k: int = 5):
    """
    類似文書を検索
    """
    query_vec = embed_text(query)
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)
    return results
