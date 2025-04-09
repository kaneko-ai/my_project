# streamlit_app.py（自動推薦 vs 手動モデル 比較対応）

import streamlit as st
import pandas as pd
from api_clients.pubmed_client import fetch_pubmed_articles
from api_clients.arxiv_biorxiv_client import fetch_arxiv_articles, fetch_biorxiv_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log
from utils.model_recommender import recommend_model
from fpdf import FPDF
import io

st.set_page_config(page_title="論文要約ツール", layout="centered")
st.title("📄 論文要約 & モデル比較ツール")
st.markdown("キーワードから論文を検索し、**自動推薦モデルと手動選択モデル**で要約を比較し、保存できます。")

# --- 検索対象とキーワード入力 ---
source = st.selectbox("📚 検索対象:", ["PubMed", "arXiv", "bioRxiv"])
query = st.text_input("🔍 検索キーワードを入力")

# --- モデル選択（複数） ---
selected_models = st.multiselect(
    "🧠 手動で使用する要約モデルを選択（任意）:",
    ["default", "bart", "pegasus"],
    default=[]
)

if st.button("検索して比較要約！"):
    if not query:
        st.warning("検索キーワードを入力してください。")
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

                for idx, article in enumerate(articles):
                    st.markdown("---")
                    st.subheader(f"📄 {article.title}")
                    st.write(article.abstract)

                    # 🔁 推奨モデル判定
                    recommended_model = recommend_model(article.abstract)
                    st.info(f"🔍 自動推薦モデル: `{recommended_model}`")

                    # 📚 実行対象モデル（重複排除）
                    all_models = list(set([recommended_model] + selected_models))

                    # 🔁 要約実行（手動＋自動推薦）
                    model_summaries = {}
                    for model in all_models:
                        with st.spinner(f"{model} で要約中..."):
                            summary = summarize_text(article.abstract, model=model)
                            model_summaries[model] = summary
                            save_log(f"検索: {query} | モデル: {model} | タイトル: {article.title} | 要約: {summary}")

                    # 📊 表で比較表示
                    summary_df = pd.DataFrame.from_dict(model_summaries, orient='index', columns=["要約"])
                    summary_df.index.name = "モデル"
                    st.dataframe(summary_df)

                    # 保存用に格納
                    summary_data.append({
                        "タイトル": article.title,
                        **model_summaries
                    })

                # --- ダウンロード（CSV） ---
                df = pd.DataFrame(summary_data)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ 比較結果をCSVで保存", csv, "summary_comparison.csv", "text/csv")

                # --- ダウンロード（PDF） ---
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for row in summary_data:
                    pdf.multi_cell(0, 10, f"タイトル: {row['タイトル']}", border=0)
                    for model in all_models:
                        summary_text = row.get(model, "（なし）")
                        pdf.multi_cell(0, 10, f"[{model}]: {summary_text}\n", border=0)
                    pdf.ln()
                pdf_buffer = io.BytesIO()
                pdf.output(pdf_buffer)
                pdf_buffer.seek(0)
                st.download_button("⬇️ PDFで保存", pdf_buffer, "summary_comparison.pdf", "application/pdf")
