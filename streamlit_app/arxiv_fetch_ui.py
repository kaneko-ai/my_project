import streamlit as st
from api_clients.arxiv_biorxiv_client import fetch_arxiv_articles

st.title("📄 arXiv論文取得ツール")

query = st.text_input("🔍 検索キーワードを入力（例: GPT, BERT, CD73）", "natural language processing")
max_results = st.slider("取得件数", min_value=1, max_value=50, value=10)

if st.button("📥 論文を取得"):
    try:
        with st.spinner("論文を取得中..."):
            results = fetch_arxiv_articles(query, max_results)
        st.success(f"{len(results)} 件の論文を取得しました！")
        for i, paper in enumerate(results, 1):
            st.markdown(f"{i}. [{paper['title']}]({paper['url']})")
    except Exception as e:
        st.error(f"取得に失敗しました: {e}")
