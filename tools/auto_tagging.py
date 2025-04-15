import spacy

# 分野ごとのキーワード辞書（必要に応じて追加可能）
CATEGORY_KEYWORDS = {
    "LLM": ["language model", "GPT", "transformer"],
    "医療": ["patient", "clinical", "health", "disease", "biomedical"],
    "教育": ["education", "learning", "school", "student"],
    "金融": ["finance", "bank", "stock", "trading", "risk"],
    "法律": ["law", "legal", "regulation", "compliance"]
}

# spaCy英語モデルを読み込み
nlp = spacy.load("en_core_web_sm")

def auto_detect_tags(text):
    """要約文などから分野タグを自動判定して返す"""
    doc = nlp(text.lower())  # 小文字化して形態素解析
    detected = set()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for token in doc:
            if token.text in keywords:
                detected.add(category)

    return list(detected)
