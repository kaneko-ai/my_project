import os
import fitz  # PyMuPDF
import sqlite3
from transformers import pipeline
from multi_stage_summarizer import multi_stage_summarize
from classify_field_bert import classify_field

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return " ".join(page.get_text() for page in doc)

def summarize_and_store(pdf_path, db_path="data/papers.db"):
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    full_text = extract_text_from_pdf(pdf_path)
    if len(full_text.strip()) < 500:
        print("⚠️ 内容が少なすぎます")
        return

    # 中間・最終要約
    mids = multi_stage_summarize(full_text)
    final_summary = summarizer(full_text[:4000])[0]["summary_text"]

    # 分類（分野）
    field, field_score = classify_field(title, final_summary)

    # DB保存
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO papers (doi, title, summary, mid_summary, total_score, field, field_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        None,
        title,
        final_summary,
        str(mids),
        0,
        field,
        field_score
    ))
    conn.commit()
    conn.close()
    print(f"✅ {title} を保存しました")

if __name__ == "__main__":
    summarize_and_store("data/sample.pdf")
