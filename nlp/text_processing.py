# nlp/text_processing.py
import spacy
import nltk
import pysbd

def load_spacy_model():
    """spacy の英語モデルをロードして返します。"""
    return spacy.load("en_core_web_sm")

def split_sentences(text: str) -> list:
    """テキストを文に分割します。pysbd が使えなければ nltk を使います。"""
    try:
        segmenter = pysbd.Segmenter(language="en", clean=True)
        return segmenter.segment(text)
    except Exception:
        return nltk.sent_tokenize(text)

def truncate_text(text: str, max_length: int = 1000) -> str:
    """テキストが長すぎる場合、指定の長さで切り捨てます。"""
    return text if len(text) <= max_length else text[:max_length-3] + "..."
