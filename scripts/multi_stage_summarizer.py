import os
import fitz  # PyMuPDF
from transformers import pipeline

# === モデル準備（無料）===
summarizer = pipeline("summarization", model="google/pegasus-xsum")

# === ステージ1：PDF → テキスト分割 ===
def extract_and_split(pdf_path: str, chunk_size: int = 1000) -> list[str]:
    doc = fitz.open(pdf_path)
    full_text = "".join([page.get_text() for page in doc])
    chunks = []
    for i in range(0, len(full_text), chunk_size):
        chunks.append(full_text[i:i+chunk_size])
    return chunks

# === ステージ2：各チャンクを小要約 ===
def summarize_chunks(chunks: list[str]) -> list[str]:
    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            summary = summarizer(chunk, max_length=120, min_length=30, do_sample=False)[0]["summary_text"]
            summaries.append(summary)
            print(f"✅ Chunk {i+1}/{len(chunks)} 要約完了")
        except Exception as e:
            print(f"⚠️ Chunk {i+1} 要約失敗: {e}")
    return summaries

# === ステージ3：中間要約をまとめて再要約 ===
def summarize_combined(summaries: list[str]) -> str:
    joined = " ".join(summaries)
    final = summarizer(joined[:1024], max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    return final

# === メイン処理 ===
def multi_stage_summarize(pdf_path: str, save_path: str):
    print(f"\n📄 対象PDF: {pdf_path}")

    chunks = extract_and_split(pdf_path)
    print(f"📚 テキスト分割完了（{len(chunks)}チャンク）")

    chunk_summaries = summarize_chunks(chunks)
    mid_summary_path = save_path.replace(".txt", "_mid.txt")
    with open(mid_summary_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(chunk_summaries))
    print(f"📄 中間要約保存: {mid_summary_path}")

    final_summary = summarize_combined(chunk_summaries)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(final_summary)
    print(f"🎯 最終要約保存完了: {save_path}")

# === 使用例 ===
if __name__ == "__main__":
    pdf_path = "data/pdfs/10.1038_s41586-020-2649-2.pdf"  # あらかじめDL済み
    save_path = "data/summaries/multi_summary.txt"
    multi_stage_summarize(pdf_path, save_path)
