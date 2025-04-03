# nlp/text_processing.py
import spacy
import pysbd
import nltk

def load_spacy_model():
    """
    spaCy の英語モデル en_core_web_sm を読み込みます。
    モデルが存在しない場合は自動でダウンロードします。
    """
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        import os
        os.system("python -m spacy download en_core_web_sm")
        return spacy.load("en_core_web_sm")

def split_sentences(text: str) -> list:
    """
    pysbd を使って文章を文単位に分割します。
    pysbd が使えない場合は、nltk で分割します。
    """
    try:
        segmenter = pysbd.Segmenter(language="en", clean=True)
        return segmenter.segment(text)
    except Exception:
        return nltk.sent_tokenize(text)

def summarize_text(text: str, max_length: int = 150) -> str:
    """
    Transformer を用いた要約処理を行う予定ですが、
    今回は簡単な例として、文章が長すぎる場合は単に切り詰めるだけにしています。
    """
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text
