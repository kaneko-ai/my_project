import streamlit as st
import os
import subprocess

st.set_page_config(page_title="再学習ダッシュボード", layout="wide")

st.title("🛠️ 誤分類・再学習 管理ダッシュボード")

if st.button("1️⃣ 誤分類データ抽出"):
    subprocess.run(["python3", "extract_misclassified.py"])
    st.success("誤分類データを抽出しました。")

if st.button("2️⃣ モデル再学習"):
    subprocess.run(["python3", "retrain_pipeline.py"])
    st.success("再学習モデルを保存しました。")

if st.button("3️⃣ レポート生成"):
    subprocess.run(["python3", "generate_report.py"])
    st.success("PDFレポートを出力しました。")

if st.button("📂 出力フォルダを表示"):
    files = os.listdir("outputs")
    for f in files:
        st.markdown(f"📄 {f}")
