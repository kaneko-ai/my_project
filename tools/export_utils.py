import json
import os
import csv

DB_PATH = "db/paper_db.jsonl"

def export_top_papers_json(output_path="export/top_papers.jsonl", top_k=20):
    if not os.path.exists(DB_PATH):
        return "❌ DBファイルが見つかりません"

    with open(DB_PATH, "r", encoding="utf-8") as f:
        all_papers = [json.loads(line) for line in f if line.strip()]

    # スコア順に並べて上位を抽出
    top_papers = sorted(all_papers, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as out:
        for paper in top_papers:
            export_item = {
                "title": paper.get("title", ""),
                "summary": paper.get("abstract", ""),
                "score": paper.get("score", 0),
                "year": paper.get("meta", {}).get("year", ""),
                "citations": paper.get("meta", {}).get("citations", 0),
                "journal_score": paper.get("meta", {}).get("journal_score", 0)
            }
            out.write(json.dumps(export_item, ensure_ascii=False) + "\n")

    return f"✅ エクスポート成功！→ {output_path}"

def export_top_papers_csv(output_path="export/top_papers.csv", top_k=20):
    if not os.path.exists(DB_PATH):
        return "❌ DBファイルが見つかりません"

    with open(DB_PATH, "r", encoding="utf-8") as f:
        all_papers = [json.loads(line) for line in f if line.strip()]

    top_papers = sorted(all_papers, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["title", "summary", "score", "year", "citations", "journal_score"])
        writer.writeheader()
        for paper in top_papers:
            writer.writerow({
                "title": paper.get("title", ""),
                "summary": paper.get("abstract", ""),
                "score": paper.get("score", 0),
                "year": paper.get("meta", {}).get("year", ""),
                "citations": paper.get("meta", {}).get("citations", 0),
                "journal_score": paper.get("meta", {}).get("journal_score", 0)
            })

    return f"✅ CSVエクスポート完了: {output_path}"

def export_chatgpt_prompts(output_path="export/chatgpt_prompts.jsonl", top_k=20):
    if not os.path.exists(DB_PATH):
        return "❌ DBファイルが見つかりません"

    with open(DB_PATH, "r", encoding="utf-8") as f:
        all_papers = [json.loads(line) for line in f if line.strip()]

    top_papers = sorted(all_papers, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as out:
        for paper in top_papers:
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")

            prompt_item = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"この論文の要点は？\nタイトル: {title}"
                    },
                    {
                        "role": "assistant",
                        "content": f"この論文は以下の内容を扱っています：\n{abstract}"
                    }
                ]
            }

            out.write(json.dumps(prompt_item, ensure_ascii=False) + "\n")

    return f"✅ ChatGPTプロンプト形式でエクスポート完了: {output_path}"
