import sqlite3

conn = sqlite3.connect("data/papers.db")
cur = conn.cursor()

print("📊 スコア80点以上の論文:")
for row in cur.execute("SELECT title, total_score FROM papers WHERE total_score >= 80 ORDER BY total_score DESC"):
    print(f"- {row[0]} ({row[1]:.1f}点)")

print("\n🧠 AI関連トピックの論文:")
for row in cur.execute("SELECT title, concepts FROM papers WHERE concepts LIKE '%Artificial Intelligence%'"):
    print(f"- {row[0]}")

conn.close()
