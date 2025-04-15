import pdfplumber
from transformers import pipeline

summarizer = pipeline("summarization", model="google/flan-t5-base", tokenizer="google/flan-t5-base")

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

def summarize_text(text, max_tokens=512):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = [summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks[:3]]
    return "\n".join(summaries)
