# streamlit_app.py（モデル比較対応）

import streamlit as st
import pandas as pd
from api_clients.pubmed_client import fetch_pubmed_articles
from api_clients.arxiv_biorxiv_client import fetch_arxiv_articles, fetch_biorxiv_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log
from fpdf import FPDF
import io

st.set_page_config(page_title="論文要約ツール", layout="centered")
st.title("📄 論文要約 & モデル比較ツール")
st.markdown("キーワードから論文を検索し、複数モデルで要約比較 & 保存できます。")

# --- 検索対象とキーワード入力 ---
source = st.selectbox("📚 検索対象:", ["PubMed", "arXiv", "bioRxiv"])
query = st.text_input("🔍 検索キーワードを入力")

# --- モデル選択（複数） ---
selected_models = st.multiselect(
    "🧠 使用する要約モデルを選択:",
    ["gpt", "bart", "default"],
    default=["default"]
)

if st.button("検索して比較要約！"):
    if not query or not selected_models:
        st.warning("キーワードとモデルを選択してください。")
    else:
        with st.spinner(f"{source} から論文取得中..."):
            if source == "PubMed":
                articles = fetch_pubmed_articles(query)
            elif source == "arXiv":
                articles = fetch_arxiv_articles(query)
            elif source == "bioRxiv":
                articles = fetch_biorxiv_articles(query)
            else:
                articles = []

            if not articles:
                st.error("論文が見つかりませんでした。")
            else:
                summary_data = []
                for article in articles:
                    st.markdown("---")
                    st.subheader(f"📄 {article.title}")
                    st.write(article.abstract)

                    model_summaries = {}
                    for model in selected_models:
                        summary = summarize_text(article.abstract, model=model)
                        model_summaries[model] = summary
                        save_log(f"検索: {query} | モデル: {model} | タイトル: {article.title} | 要約: {summary}")

                    # 表形式で比較表示
                    summary_df = pd.DataFrame.from_dict(model_summaries, orient='index', columns=["要約"])
                    st.dataframe(summary_df)

                    # PDF/CSV 保存用に記録
                    summary_data.append({
                        "タイトル": article.title,
                        **model_summaries
                    })

                # --- ダウンロード ---
                df = pd.DataFrame(summary_data)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ 比較結果をCSVで保存", csv, "summary_comparison.csv", "text/csv")

                # PDF出力
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for row in summary_data:
                    pdf.multi_cell(0, 10, f"タイトル: {row['タイトル']}", border=0)
                    for model in selected_models:
                        pdf.multi_cell(0, 10, f"[{model}]: {row.get(model)}\n", border=0)
                    pdf.ln()
                pdf_buffer = io.BytesIO()
                pdf.output(pdf_buffer)
                pdf_buffer.seek(0)
                st.download_button("⬇️ PDFで保存", pdf_buffer, "summary_comparison.pdf", "application/pdf")
