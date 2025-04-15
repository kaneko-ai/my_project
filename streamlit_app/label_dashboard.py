# streamlit_app/label_dashboard.py

import streamlit as st
import sqlite3
import json
import pandas as pd
from classify_field_bert import classify_field  # BERT分類器

# === データベースから読み込み ===
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/papers.db")
    cur = conn.cursor()
    cur.execute("""
    SELECT id, title, summary, total_score, mid_summary, field, field_score, reclassified
    FROM papers
    WHERE mid_summary IS NOT NULL AND field IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    data = []
    for row in rows:
        try:
            mids = json.loads(row[4])
            labels = [m["label"] for m in mids]
            label_count = {l: labels.count(l) for l in set(labels)}
            data.append({
                "id": row[0],
                "title": row[1],
                "summary": row[2],
                "score": row[3],
                "mid_summary": mids,
                "labels": labels,
                "label_count": label_count,
                "field": row[5].lower(),
                "field_score": row[6],
                "reclassified": row[7]
            })
        except:
            continue
    return data

# === Streamlit画面構成 ===
st.set_page_config(page_title="論文構成・スコア可視化", layout="wide")
st.title("📚 論文構成 × スコア × 分野分析ダッシュボード")

data = load_data()

# === 絞り込みフィルター ===
st.sidebar.header("🔍 絞り込み条件")
min_score = st.sidebar.slider("最低スコア", 0, 100, 70)
required_labels = st.sidebar.multiselect(
    "含めたいセクション", ["導入", "方法", "結果", "結論"]
)
selected_fields = st.sidebar.multiselect(
    "対象分野を選択", sorted(set(d["field"] for d in data)), default=None
)

# === フィルタ適用 ===
filtered = [
    d for d in data
    if d["score"] >= min_score
    and all(label in d["labels"] for label in required_labels)
    and (not selected_fields or d["field"] in selected_fields)
]

st.markdown(f"🎯 条件に一致した論文数: **{len(filtered)}件**")

# === 分野別 構成ラベル傾向 ===
st.subheader("🔬 分野別 構成ラベル出現傾向")

label_keys = ["導入", "方法", "結果", "結論"]
field_data = {}

for item in filtered:
    field = item["field"]
    if field not in field_data:
        field_data[field] = []
    field_data[field].append(item["label_count"])

field_df = pd.DataFrame(columns=label_keys)

for f, counts in field_data.items():
    df = pd.DataFrame(counts).fillna(0)
    avg = df.mean().reindex(label_keys, fill_value=0)
    field_df.loc[f] = avg

st.dataframe(field_df)
st.bar_chart(field_df.T)

# === 分野別 平均スコア ===
st.subheader("🎯 分野別 平均スコア比較")

field_scores = {}
for item in filtered:
    field = item["field"]
    if field not in field_scores:
        field_scores[field] = []
    field_scores[field].append(item["score"])

avg_scores = {field: sum(scores)/len(scores) for field, scores in field_scores.items()}
avg_score_df = pd.DataFrame.from_dict(avg_scores, orient='index', columns=["平均スコア"])

st.dataframe(avg_score_df)
st.bar_chart(avg_score_df)

# === 論文一覧 ===
st.subheader("📄 論文一覧")

for paper in filtered:
    with st.expander(f"📌 {paper['title']}（スコア: {paper['score']:.1f} | 分野: {paper['field']}）"):
        for m in paper["mid_summary"]:
            st.markdown(f"**🧩 {m['label']}**: {m['summary']}")
        st.markdown(f"📜 **最終要約**: _{paper['summary']}_")

        # === 再分類機能 ===
        if st.button(f"🔁 BERTで再分類する（ID: {paper['id']}）", key=f"btn_{paper['id']}"):
            with st.spinner("BERTで再分類中..."):
                new_field, score = classify_field(paper["title"], paper["summary"])
                conn = sqlite3.connect("data/papers.db")
                cur = conn.cursor()
                cur.execute("""
                    UPDATE papers SET field = ?, field_score = ?, reclassified = 1
                    WHERE id = ?
                """, (new_field, score, paper["id"]))
                conn.commit()
                conn.close()
                st.success(f"✅ 再分類完了: {new_field}（信頼度: {score:.2f}）")
                st.experimental_rerun()

# === 教師データ出力 ===
st.subheader("📤 教師データとして出力する")

if st.button("📝 再分類済みデータをCSVで出力"):
    df_export = pd.DataFrame([
        {
            "title": d["title"],
            "summary": d["summary"],
            "field": d["field"]
        } for d in data if d["reclassified"] == 1
    ])
    df_export.to_csv("reclassified_data.csv", index=False)
    st.success("✅ 'reclassified_data.csv' を出力しました！")
