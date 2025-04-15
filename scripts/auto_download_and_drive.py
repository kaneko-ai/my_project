#!/usr/bin/env python3
"""
論文自動取得スクリプト（PubMed, arXiv, bioRxiv）
"""

from api_clients.pubmed_client import fetch_pubmed_articles
from api_clients.arxiv_biorxiv_client import ArxivClient, BioRxivClient
from tools.drive_auth import upload_files_to_drive
from tools.pdf_exporter import save_article_summaries_to_pdf

QUERY = "がん"
MAX_RESULTS = 5

def main():
    # --- PubMed 論文取得 ---
    print("🔍 PubMed 論文検索中...")
    pubmed_articles = fetch_pubmed_articles(QUERY, MAX_RESULTS)

    # --- arXiv 論文取得 ---
    print("🔍 arXiv 論文検索中...")
    arxiv_client = ArxivClient()
    arxiv_articles = arxiv_client.search(QUERY, MAX_RESULTS)

    # --- bioRxiv 論文取得 ---
    print("🔍 bioRxiv 論文検索中...")
    biorxiv_client = BioRxivClient()
    biorxiv_articles = biorxiv_client.search(QUERY, MAX_RESULTS)

    # --- PDF 出力 ---
    print("📄 PDF に出力中...")
    all_articles = pubmed_articles + arxiv_articles + biorxiv_articles
    pdf_path = save_article_summaries_to_pdf(all_articles, filename="output/articles.pdf")

    # --- Google Drive アップロード（必要であれば） ---
    print("☁️ Google Drive にアップロード中...")
    upload_files_to_drive([pdf_path])

    print("✅ 全処理が完了しました！")

if __name__ == "__main__":
    main()
