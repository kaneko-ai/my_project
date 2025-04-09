# streamlit_app.py

import streamlit as st
import pandas as pd
from api_clients.pubmed_client import fetch_pubmed_articles
from api_clients.arxiv_biorxiv_client import fetch_arxiv_articles, fetch_biorxiv_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log
from fpdf import FPDF
import io

st.set_page_config(page_title="論文要約ツール", layout="centered")
st.title("📄 PubMed / arXiv / bioRxiv 論文要約 & 保存ツール")
st.markdown("キーワードから論文を検索し、要約結果をCSV/PDFで保存します。")

# 🔽 検索対象選択（PubMed / arXiv / bioRxiv）
source = st.selectbox("📚 検索対象を選択:", ["PubMed", "arXiv", "bioRxiv"])
query = st.text_input("🔍 検索キーワードを入力")

if st.button("検索して要約！"):
    if not query:
        st.warning("検索キーワードを入力してください。")
    else:
        with st.spinner(f"{source} から論文を取得して要約中..."):
            # 🔄 検索対象に応じた関数呼び出し
            if source == "PubMed":
                articles = fetch_pubmed_articles(query)
            elif source == "arXiv":
                articles = fetch_arxiv_articles(query)
            elif source == "bioRxiv":
                articles = fetch_biorxiv_articles(query)
            else:
                st.error("無効な検索対象です。")
                articles = []

            if not articles:
                st.error("論文が見つかりませんでした。")
            else:
                results = []
                summaries_text = ""

                for article in articles:
                    summary = summarize_text(article.abstract)
                    results.append({
                        "タイトル": article.title,
                        "要約": summary
                    })
                    summaries_text += f"📝【{article.title}】\n{summary}\n\n"
                    save_log(f"検索: {query} | 対象: {source} | タイトル: {article.title} | 要約: {summary}")

                df = pd.DataFrame(results)

                st.success(f"{len(results)} 件の要約を取得しました！")
                st.text_area("📑 要約結果", summaries_text, height=300)

                # CSVダウンロード
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ CSVでダウンロード", csv, "summary.csv", "text/csv")

                # PDFダウンロード
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for row in results:
                    pdf.multi_cell(0, 10, f"タイトル: {row['タイトル']}\n要約: {row['要約']}\n", border=0)
                    pdf.ln()
                pdf_buffer = io.BytesIO()
                pdf.output(pdf_buffer)
                pdf_buffer.seek(0)
                st.download_button("⬇️ PDFでダウンロード", pdf_buffer, "summary.pdf", "application/pdf")
