import sqlite3
import json

def load_summary_scores():
    conn = sqlite3.connect("data/papers.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT title, total_score, mid_summary
    FROM papers
    WHERE mid_summary IS NOT NULL AND total_score IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    data = []
    for title, score, mid_json in rows:
        try:
            mid_data = json.loads(mid_json)
            labels = [item["label"] for item in mid_data if "label" in item]
            data.append({
                "title": title,
                "score": score,
                "labels": labels,
                "label_count": {l: labels.count(l) for l in set(labels)}
            })
        except:
            continue
    return data

if __name__ == "__main__":
    data = load_summary_scores()
    sorted_data = sorted(data, key=lambda x: x["score"], reverse=True)

    print("\n🏆 スコア上位論文ランキング:")
    for item in sorted_data[:10]:  # 上位10件
        print(f"\n🔹 {item['title']}")
        print(f"  - スコア: {item['score']:.1f}")
        print(f"  - セクション構成: {item['label_count']}")
