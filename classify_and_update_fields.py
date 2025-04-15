import sqlite3
from classify_field_bert import classify_field  # ← BERT対応版

# DB接続
conn = sqlite3.connect("data/papers.db")
cur = conn.cursor()

# 未分類データ取得
cur.execute("SELECT id, title, summary FROM papers WHERE field IS NULL OR field = ''")
rows = cur.fetchall()
print(f"📚 分類対象: {len(rows)} 件")

for id_, title, summary in rows:
    try:
        field, score = classify_field(title or "", summary or "")
        cur.execute("UPDATE papers SET field = ?, field_score = ? WHERE id = ?", (field, score, id_))
        print(f"✅ ID:{id_} → {field}（信頼度: {score:.2f}）")
    except Exception as e:
        print(f"❌ ID:{id_} でエラー: {e}")

conn.commit()
conn.close()
print("🎉 BERT分類と保存完了！")
