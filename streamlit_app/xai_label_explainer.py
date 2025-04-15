import streamlit as st
import pandas as pd
import pickle
import eli5
from eli5.sklearn import explain_prediction

# === モデル読み込み ===
with open("models/structure_label_model_retrained.pkl", "rb") as f:
    model_data = pickle.load(f)

vec = model_data["tfidf"]
clf = model_data["clf"]

st.set_page_config(page_title="AIの判断根拠表示 (XAI)", layout="centered")
st.title("🔍 AIのラベル分類 根拠表示")

# === 入力エリア ===
text = st.text_area("判定理由を見たい要約を貼り付けてください", height=200)

if st.button("🧠 分析を実行"):
    if text.strip():
        html = eli5.format_as_html(
            explain_prediction(clf, text, vec=vec)
        )
        st.components.v1.html(html, height=400, scrolling=True)
    else:
        st.warning("テキストを入力してください。")
