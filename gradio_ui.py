# gradio_ui.py

import gradio as gr
import pandas as pd
from api_clients.pubmed_client import fetch_pubmed_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log

from fpdf import FPDF
import tempfile
import os


def generate_pdf_file(records):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", fname=None)
    pdf.set_font("Arial", size=12)

    for record in records:
        pdf.multi_cell(0, 10, f"タイトル: {record['タイトル']}\n要約: {record['要約']}\n", border=0)
        pdf.ln()

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name


def search_and_summarize(query: str):
    if not query:
        return "キーワードを入力してください", "", None, None

    articles = fetch_pubmed_articles(query)
    if not articles:
        return "論文が見つかりませんでした", "", None, None

    summaries = []
    full_log = []
    records = []

    for article in articles:
        summary = summarize_text(article.abstract)
        summaries.append(f"📝【{article.title}】\n{summary}\n")
        full_log.append(f"検索語: {query} / タイトル: {article.title} / 要約: {summary}")

        records.append({
            "タイトル": article.title,
            "要約": summary
        })

    for line in full_log:
        save_log(line)

    # CSV出力
    df = pd.DataFrame(records)
    tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="")
    df.to_csv(tmp_csv.name, index=False)
    tmp_csv.close()

    # PDF出力
    pdf_path = generate_pdf_file(records)

    return "\n\n".join(summaries), "\n".join(full_log), tmp_csv.name, pdf_path


# Gradio UI
iface = gr.Interface(
    fn=search_and_summarize,
    inputs=gr.Textbox(label="PubMed 検索キーワード"),
    outputs=[
        gr.Textbox(label="要約結果"),
        gr.Textbox(label="ログ内容"),
        gr.File(label="CSVダウンロード"),
        gr.File(label="PDFダウンロード")
    ],
    title="PubMed 論文要約 & 保存ツール",
    description="キーワードから論文を検索し、要約をCSV・PDFで出力します。",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()
