import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="教師データラベリングツール", layout="wide")
st.title("📝 教師データ拡張ツール（論文分野ラベル付け）")

# CSV出力先
SAVE_PATH = "data/field_train.csv"
os.makedirs("data", exist_ok=True)

# データベースからデータ取得
def load_papers():
    conn = sqlite3.connect("data/papers.db")
    cur = conn.cursor()
    cur.execute("SELECT id, title, summary, field FROM papers")
    rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["id", "title", "summary", "field"])

df = load_papers()

# 表示対象をフィルタ（全件または未分類のみ）
filter_mode = st.sidebar.selectbox("表示対象", ["未分類のみ", "すべて表示"])
if filter_mode == "未分類のみ":
    df = df[df["field"].isna() | (df["field"] == "")]

# ラベル候補
field_options = ["nlp", "biomed", "physics", "earth", "other"]

st.markdown(f"📚 表示中の論文数: {len(df)} 件")

# 入力UI
for i, row in df.iterrows():
    with st.expander(f"📄 {row['title'][:80]}..."):
        st.markdown(f"**📝 概要**: {row['summary'][:300]}...")
        selected_field = st.selectbox(
            f"分野を選んでください（ID: {row['id']}）",
            field_options,
            key=f"select_{row['id']}"
        )

        if st.button(f"✅ 教師データに追加 (ID: {row['id']})", key=f"btn_{row['id']}"):
            # データを1行追加
            new_row = {
                "title": row["title"],
                "abstract": row["summary"],
                "field": selected_field
            }

            # CSVファイルが存在しなければ新規作成
            if not os.path.exists(SAVE_PATH):
                pd.DataFrame([new_row]).to_csv(SAVE_PATH, index=False)
            else:
                pd.DataFrame([new_row]).to_csv(SAVE_PATH, mode="a", header=False, index=False)

            st.success("✅ 教師データに保存しました！")
