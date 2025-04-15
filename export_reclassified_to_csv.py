import sqlite3
import pandas as pd

conn = sqlite3.connect("data/papers.db")
cur = conn.cursor()

# 再分類された論文だけ取得
cur.execute("""
    SELECT title, summary, field FROM papers
    WHERE reclassified = 1
""")
rows = cur.fetchall()
conn.close()

# CSVとして保存
df = pd.DataFrame(rows, columns=["title", "abstract", "field"])
df.to_csv("data/field_train.csv", mode="a", header=False, index=False)

print(f"✅ {len(df)} 件の再分類済みデータを教師データに追加しました！")
