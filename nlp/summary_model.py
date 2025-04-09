# nlp/summary_model.py
from transformers import pipeline

# Hugging Face の要約パイプライン（scibertではなくpegasusやbartを使用）
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str, max_length: int = 200) -> str:
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]["summary_text"]
