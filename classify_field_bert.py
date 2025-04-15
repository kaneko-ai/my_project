from typing import Tuple  # Python 3.8 対応のために必要
from transformers import pipeline

# BERTベースの分類器パイプラインを準備（HuggingFaceの zero-shot-classification を利用）
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# 分類したいラベル（論文分野など）
CANDIDATE_LABELS = ["自然言語処理", "機械学習", "医学", "生物学", "神経科学", "バイオインフォマティクス", "ロボティクス"]

def classify_field(title: str, summary: str) -> Tuple[str, float]:
    """
    タイトルと要約から、論文の分野をBERTモデルで分類する関数
    戻り値: (予測分野, スコア)
    """
    # タイトルと要約を1つにまとめて判定文として使用
    input_text = f"{title}. {summary}"

    # 分類実行
    result = classifier(input_text, CANDIDATE_LABELS)

    # 最もスコアが高いラベルとそのスコアを返す
    return result["labels"][0], result["scores"][0]
