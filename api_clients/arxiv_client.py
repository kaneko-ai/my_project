# -*- coding: utf-8 -*-
"""
arXiv API クライアント
"""

import feedparser

def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    base_url = "http://export.arxiv.org/api/query"
    search_url = f"{base_url}?search_query=all:{query}&start=0&max_results={max_results}"

    feed = feedparser.parse(search_url)
    results = []

    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "doi": entry.get("arxiv_doi", None),  # DOIがある論文のみOpenAlex補完可能
            "journal": "arXiv"
        })

    return results
