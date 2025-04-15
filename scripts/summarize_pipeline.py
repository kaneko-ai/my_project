import os
import requests
import fitz  # PyMuPDF
from transformers import pipeline

# === 要約モデル準備 ===
print("🧠 HuggingFaceモデル読込中...")
summarizer = pipeline("summarization", model="google/pegasus-xsum")

# === ディレクトリ確認 ===
os.makedirs("data/pdfs", exist_ok=True)
os.makedirs("data/summaries", exist_ok=True)

# === 論文DOI設定（例）===
doi_list = [
    "10.1038/s41586-020-2649-2",  # Nature 論文（PDF取得できるDOI）
    "10.1101/2020.02.12.20022472"  # bioRxiv
]

def download_pdf(doi: str) -> str | None:
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/pdf"}
    try:
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        if "application/pdf" not in res.headers.get("Content-Type", ""):
            print(f"⚠️ PDFが取得できません: {doi}")
            return None
        filename = f"data/pdfs/{doi.replace('/', '_')}.pdf"
        with open(filename, "wb") as f:
            f.write(res.content)
        return filename
    except Exception as e:
        print(f"❌ ダウンロード失敗: {doi} ({e})")
        return None

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def summarize_text(text: str) -> str:
    max_input = 1024
    chunks = text[:max_input]  # 長すぎ防止（1段階要約ならこれで十分）
    result = summarizer(chunks, max_length=120, min_length=30, do_sample=False)
    return result[0]["summary_text"]

# === メイン処理 ===
for doi in doi_list:
    print(f"\n📄 処理中: {doi}")
    pdf_path = download_pdf(doi)
    if not pdf_path:
        continue

    text = extract_text(pdf_path)
    if not text:
        print("❌ PDFからテキストが抽出できませんでした")
        continue

    summary = summarize_text(text)

    # 保存
    summary_path = f"data/summaries/summary_{doi.replace('/', '_')}.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ 要約保存完了: {summary_path}")
