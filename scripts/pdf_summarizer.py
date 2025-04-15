import os
import requests
import fitz  # PyMuPDF

def download_pdf(doi: str, save_dir="data/pdfs"):
    os.makedirs(save_dir, exist_ok=True)
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/pdf"}

    try:
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        if "application/pdf" not in res.headers.get("Content-Type", ""):
            print(f"❌ PDFではありません: {doi}")
            return None

        filename = os.path.join(save_dir, doi.replace("/", "_") + ".pdf")
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"✅ PDFダウンロード成功: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️ ダウンロード失敗: {doi} ({e})")
        return None

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
