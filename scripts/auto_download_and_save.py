import os
import feedparser
import requests
from datetime import datetime
from scripts.history_logger import log_download

SAVE_DIR = "papers"
os.makedirs(SAVE_DIR, exist_ok=True)

def download_papers_by_keyword(keyword: str, max_results: int = 5) -> list:
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{keyword}&start=0&max_results={max_results}"
    response = feedparser.parse(base_url + query)

    downloaded_files = []
    for entry in response.entries:
        title = entry.title.replace(" ", "_").replace("/", "_")
        pdf_url = entry.id.replace("abs", "pdf") + ".pdf"
        filename = f"{title[:50]}.pdf"  # 長いタイトルはカット
        filepath = os.path.join(SAVE_DIR, filename)

        if not os.path.exists(filepath):
            r = requests.get(pdf_url)
            with open(filepath, "wb") as f:
                f.write(r.content)
            downloaded_files.append(filename)

    # 履歴ログを記録
    log_download(keyword=keyword, file_list=downloaded_files)

    return downloaded_files
