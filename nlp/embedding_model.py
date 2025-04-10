# nlp/embedding_model.py

from sentence_transformers import SentenceTransformer

# 無料モデルで軽量・高精度
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str):
    """
    文章をベクトルに変換
    """
    return model.encode(text, convert_to_tensor=False)  # numpy arrayで返す
