# gradio_ui.py

import gradio as gr
import pandas as pd
from api_clients.pubmed_client import fetch_pubmed_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log

import tempfile
import os

def search_and_summarize_with_csv(query: str):
    if not query:
        return "キーワードを入力してください", "", None

    articles = fetch_pubmed_articles(query)
    if not articles:
        return "論文が見つかりませんでした", "", None

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

    # ログ保存（ファイルとメモリ）
    for line in full_log:
        save_log(line)

    # 一時CSVファイルを作成してパスを返す
    df = pd.DataFrame(records)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="")
    df.to_csv(tmp_file.name, index=False)
    tmp_file.close()

    return "\n\n".join(summaries), "\n".join(full_log), tmp_file.name

# Gradio UI定義
iface = gr.Interface(
    fn=search_and_summarize_with_csv,
    inputs=gr.Textbox(label="PubMed 検索キーワード"),
    outputs=[
        gr.Textbox(label="要約結果"),
        gr.Textbox(label="ログ内容"),
        gr.File(label="CSVダウンロード")
    ],
    title="PubMed 論文要約 & CSV出力ツール",
    description="キーワードから論文を検索し、要約とCSVファイルで出力します。",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()
