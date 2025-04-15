import sqlite3
import json
import os

DB_PATH = "data/papers.db"
JSON_PATH = "data/unified_evaluated.json"

# DB初期化
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS papers")
cur.execute("""
CREATE TABLE papers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doi TEXT,
  title TEXT,
  journal TEXT,
  publication_date TEXT,
  authors TEXT,
  abstract TEXT,
  citation_count INTEGER,
  concepts TEXT,
  country_codes TEXT,
  journal_quality REAL,
  citation_score REAL,
  altmetric_score REAL,
  reproducibility REAL,
  structural_score REAL,
  total_score REAL
);
""")

# JSON読み込み
with open(JSON_PATH, "r", encoding="utf-8") as f:
    papers = json.load(f)

# データ挿入
for p in papers:
    cur.execute("""
    INSERT INTO papers (
        doi, title, journal, publication_date, authors, abstract,
        citation_count, concepts, country_codes,
        journal_quality, citation_score, altmetric_score,
        reproducibility, structural_score, total_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p.get("doi"),
        p.get("title"),
        p.get("journal"),
        p.get("publication_date"),
        ", ".join(p.get("authors", [])),
        p.get("abstract"),
        p.get("citation_count", 0),
        ", ".join(p.get("concepts", [])),
        ",".join({inst.get("country_code", "") for a in p.get("authorships", []) for inst in a.get("institutions", [])}),
        p.get("journal_quality"),
        p.get("citation"),
        p.get("altmetric"),
        p.get("reproducibility"),
        p.get("structural"),
        p.get("total_score")
    ))

conn.commit()
conn.close()
print(f"✅ 論文データを {DB_PATH} に保存しました")
