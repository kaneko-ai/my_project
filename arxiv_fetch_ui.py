import streamlit as st
import sys
import os
import requests
import xml.etree.ElementTree as ET

# --- 検索パスに上の階層を追加（他モジュール用） ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- arXiv論文取得関数の定義 ---
def fetch_arxiv_articles(query="natural language processing", max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"arXiv API error: {response.status_code}")

    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    results = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        link = entry.find("atom:id", ns).text.strip()
        results.append({"title": title, "url": link})

    return results

# --- Streamlit UI定義 ---
st.set_page_config(page_title="arXiv論文取得ツール", page_icon="📄")
st.title("📄 arXiv論文取得ツール")

# 検索フォーム
query = st.text_input("🔍 検索キーワードを入力（例: GPT, BERT, CD73）", "natural language processing")
max_results = st.slider("取得件数", min_value=1, max_value=50, value=10)

# 検索実行
if st.button("📥 論文を取得"):
    try:
        with st.spinner("論文を取得中..."):
            results = fetch_arxiv_articles(query, max_results)
        st.success(f"{len(results)} 件の論文を取得しました！")

        for i, paper in enumerate(results, 1):
            st.markdown(f"**{i}. [{paper['title']}]({paper['url']})**")

    except Exception as e:
        st.error(f"取得に失敗しました: {e}")
