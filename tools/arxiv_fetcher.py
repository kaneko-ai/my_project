# tools/arxiv_fetcher.py

import feedparser
import requests
import os

def fetch_arxiv_papers(query="chatgpt", max_results=3, save_dir="papers"):
    base_url = "http://export.arxiv.org/api/query?"
    query_url = f"{base_url}search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(query_url)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    results = []
    for entry in feed.entries:
        pdf_link = next((l.href for l in entry.links if l.type == 'application/pdf'), None)
        paper_id = entry.id.split("/")[-1]
        file_path = os.path.join(save_dir, f"{paper_id}.pdf")

        if pdf_link:
            try:
                pdf_data = requests.get(pdf_link)
                with open(file_path, "wb") as f:
                    f.write(pdf_data.content)
            except Exception as e:
                print(f"❌ PDF取得エラー: {e}")
                file_path = None

        results.append({
            "title": entry.title,
            "summary": entry.summary,
            "pdf_link": pdf_link,
            "pdf_path": file_path
        })

    return results  # ← ここが超重要！
