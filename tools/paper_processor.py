# paper_processor.py
from sentence_transformers import SentenceTransformer
import json
import datetime

# ベクトル変換用モデル（事前学習済みの軽量モデル）
model = SentenceTransformer('all-MiniLM-L6-v2')

def vectorize_text(text: str):
    """文章をベクトルに変換"""
    return model.encode(text).tolist()

def compute_score(metadata: dict):
    """
    評価スコアを0～100で算出する（シンプルな重み付き）
    - 発表年: 30点
    - 被引用数: 40点
    - ジャーナル評価: 30点
    """
    year_weight = 30
    citation_weight = 40
    journal_weight = 30

    # 年スコア（2025年基準）
    current_year = datetime.datetime.now().year
    year_score = max(0, min(1, (int(metadata.get("year", current_year)) - 2015) / 10)) * year_weight

    # 被引用スコア（最大1000と想定）
    citations = int(metadata.get("citations", 0))
    citation_score = min(1, citations / 1000) * citation_weight

    # ジャーナルスコア（0～1で与えられてると想定）
    journal_quality = float(metadata.get("journal_score", 0.5))
    journal_score = journal_quality * journal_weight

    total_score = round(year_score + citation_score + journal_score, 2)
    return total_score

def process_paper(title, abstract, metadata):
    """論文のベクトルとスコアをまとめる"""
    combined_text = f"{title}. {abstract}"
    vec = vectorize_text(combined_text)
    score = compute_score(metadata)
    return {
        "title": title,
        "abstract": abstract,
        "vector": vec,
        "score": score,
        "meta": metadata
    }

# テスト用
if __name__ == "__main__":
    title = "Advances in Large Language Models"
    abstract = "We explore recent progress in transformer-based architectures for language understanding..."
    metadata = {
        "year": "2023",
        "citations": 423,
        "journal_score": 0.8
    }

    result = process_paper(title, abstract, metadata)
    print(json.dumps(result, indent=2)[:1000])
