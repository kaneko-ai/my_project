import json
import os
from sentence_transformers.util import cos_sim
import numpy as np
from collections import Counter
import pandas as pd

DB_PATH = "db/paper_db.jsonl"

def save_paper(entry):
    entry.setdefault("tags", [])
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def load_all_papers():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def search_similar_papers(query_vector, top_k=3):
    papers = load_all_papers()
    results = []
    for paper in papers:
        if "vector" not in paper:
            continue
        db_vec = np.array(paper["vector"])
        similarity = float(cos_sim(query_vector, db_vec))
        results.append({
            "title": paper["title"],
            "summary": paper["abstract"],
            "score": paper["score"],
            "similarity": similarity,
            "tags": paper.get("tags", [])
        })
    return sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]

def search_by_tag(tag: str, top_k=10):
    papers = load_all_papers()
    filtered = [p for p in papers if tag in p.get("tags", [])]
    return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

def get_tag_statistics():
    papers = load_all_papers()
    tag_counter = Counter()
    score_by_tag = {}
    for p in papers:
        tags = p.get("tags", [])
        score = p.get("score", 0)
        for tag in tags:
            tag_counter[tag] += 1
            score_by_tag.setdefault(tag, []).append(score)
    tag_stats = []
    for tag in tag_counter:
        count = tag_counter[tag]
        avg_score = round(sum(score_by_tag[tag]) / len(score_by_tag[tag]), 3)
        tag_stats.append({"タグ": tag, "件数": count, "平均スコア": avg_score})
    return pd.DataFrame(tag_stats).sort_values("件数", ascending=False)

def get_year_distribution():
    papers = load_all_papers()
    year_counter = Counter(p.get("meta", {}).get("year", "不明") for p in papers)
    return pd.DataFrame({
        "年": list(year_counter.keys()),
        "件数": list(year_counter.values())
    }).sort_values("年")
