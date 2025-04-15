import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="低信頼ラベル修正ツール", layout="wide")
st.title("⚠️ 低スコア分類 修正＆教師データ化ツール")

SAVE_PATH = "data/field_train.csv"
os.makedirs("data", exist_ok=True)

# 信頼度の閾値（ユーザー設定）
threshold = st.sidebar.slider("信頼度の上限（field_score）", 0.0, 1.0, 0.6, step=0.05)

# DBから低スコア論文を抽出
@st.cache_data
def load_low_score_papers(threshold=0.6):
    conn = sqlite3.connect("data/papers.db")
    df = pd.read_sql_query(f"""
        SELECT id, title, summary, field_score FROM papers
        WHERE field_score IS NOT NULL AND field_score < {threshold}
        ORDER BY field_score ASC
        """, conn)
    conn.close()
    return df

df = load_low_score_papers(threshold)
st.markdown(f"📉 対象論文数（スコア<{threshold}）: **{len(df)} 件**")

field_options = ["nlp", "biomed", "physics", "earth", "robotics", "other"]

# 一覧UI表示
for _, row in df.iterrows():
    with st.expander(f"📄 {row['title'][:80]}... | Score: {row['field_score']:.2f}"):
        st.markdown(row["summary"][:300] + "...")
        selected_label = st.selectbox(f"✅ 分野を選択（ID: {row['id']}）", field_options, key=f"select_{row['id']}")

        if st.button("💾 教師データに追加", key=f"add_{row['id']}"):
            new_entry = {
                "title": row["title"],
                "abstract": row["summary"],
                "field": selected_label
            }

            if not os.path.exists(SAVE_PATH):
                pd.DataFrame([new_entry]).to_csv(SAVE_PATH, index=False)
            else:
                pd.DataFrame([new_entry]).to_csv(SAVE_PATH, mode="a", header=False, index=False)

            st.success("✅ 教師データに追加されました！")
