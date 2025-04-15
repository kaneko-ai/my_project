# -*- coding: utf-8 -*-
"""
bioRxiv API クライアント（Rxivist経由）
"""

import requests

def search_biorxiv(query: str, max_results: int = 10) -> list[dict]:
    url = f"https://api.biorxiv.org/details/biorxiv/2020-01-01/3000-01-01/{max_results}"  # 日付で絞り可
    res = requests.get(url)
    data = res.json()
    results = []

    for item in data.get("collection", []):
        if query.lower() in item["title"].lower():
            results.append({
                "title": item["title"],
                "doi": item["doi"],
                "authors": item["authors"].split(";"),
                "published": item["date"],
                "abstract": item["abstract"],
                "journal": "bioRxiv"
            })
    return results
