# utils/summarizer.py

def summarizer(text: str) -> str:
    """簡易的な要約関数（今は文字数制限だけ）"""
    return text[:200] + "..." if len(text) > 200 else text
