from transformers import pipeline
import re

# 高度な要約モデル（例：facebook/bart-large-cnn）
summarizer_pipe = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_advanced(text):
    summary = summarizer_pipe(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

def extract_key_sentences(text, top_n=2):
    sentences = re.split(r'[。.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences[:top_n]  # 一旦先頭から2文だけ取る（改良可）

def classify_tags(text):
    tags = []
    text = text.lower()
    if "cancer" in text or "tumor" in text:
        tags.append("Oncology")
    if "immuno" in text:
        tags.append("Immunology")
    if "neuro" in text:
        tags.append("Neuroscience")
    if "genome" in text:
        tags.append("Genetics")
    return tags or ["General"]
