# -*- coding: utf-8 -*-
"""
全論文データベース統合パイプライン
"""

import os, json
from api_clients.pubmed_client import search_pubmed, fetch_pubmed_details
from api_clients.arxiv_client import search_arxiv
from api_clients.biorxiv_client import search_biorxiv
from api_clients.openalex_client import fetch_openalex_data_by_doi, extract_metadata_from_openalex
from utils.evaluator import evaluate_paper

os.makedirs("data", exist_ok=True)

query = "artificial intelligence in medicine"
max_results = 5

# === 各DBから論文取得 ===
papers_all = []

## PubMed
pmids = search_pubmed(query, max_results)
pubmed_papers = fetch_pubmed_details(pmids)
papers_all += pubmed_papers

## arXiv
arxiv_papers = search_arxiv(query, max_results)
papers_all += arxiv_papers

## bioRxiv
biorxiv_papers = search_biorxiv(query, max_results)
papers_all += biorxiv_papers

# 保存：raw
with open("data/unified_raw.json", "w", encoding="utf-8") as f:
    json.dump(papers_all, f, indent=2, ensure_ascii=False)

# === OpenAlex補完 → 評価 ===
evaluated = []
for paper in papers_all:
    doi = paper.get("doi")
    oa_meta = {}
    if doi:
        oa_data = fetch_openalex_data_by_doi(doi)
        oa_meta = extract_metadata_from_openalex(oa_data)

    paper.update(oa_meta)
    score = evaluate_paper(paper)
    paper.update(score)
    evaluated.append(paper)

# 保存：評価付き
with open("data/unified_evaluated.json", "w", encoding="utf-8") as f:
    json.dump(evaluated, f, indent=2, ensure_ascii=False)

print("✅ 統合評価パイプライン完了 → data/unified_evaluated.json に出力済み")
