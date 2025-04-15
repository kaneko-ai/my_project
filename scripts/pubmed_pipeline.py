import os
from api_clients.pubmed_client import search_pubmed, fetch_pubmed_details
from utils.evaluator import evaluate_paper
from classify_field_bert import classify_field
import sqlite3
import json

def run_pipeline(query="cancer immunotherapy", max_results=5, db_path="data/papers.db"):
    pmids = search_pubmed(query, max_results=max_results)
    papers = fetch_pubmed_details(pmids)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for paper in papers:
        title = paper.get("title")
        summary = paper.get("abstract")
        if not summary or len(summary) < 100:
            continue

        # 評価スコア
        scores = evaluate_paper(paper)
        total_score = scores.get("total_score", 0)

        # 分類
        field, field_score = classify_field(title, summary)

        cur.execute("""
            INSERT OR IGNORE INTO papers
            (doi, title, summary, mid_summary, total_score, field, field_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paper.get("doi"),
            title,
            summary,
            None,
            total_score,
            field,
            field_score
        ))

    conn.commit()
    conn.close()
    print(f"✅ {len(papers)} 論文を保存しました。")

if __name__ == "__main__":
    run_pipeline()
