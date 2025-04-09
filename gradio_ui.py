# gradio_ui.py

import gradio as gr
from api_clients.pubmed_client import fetch_pubmed_articles
from nlp.summary_model import summarize_text
from utils.log_manager import save_log

def search_and_summarize(query: str):
    if not query:
        return "キーワードを入力してください", ""

    # PubMedから記事取得
    articles = fetch_pubmed_articles(query)

    if not articles:
        return "論文が見つかりませんでした", ""

    summaries = []
    full_log = []

    for article in articles:
        summary = summarize_text(article.abstract)
        summaries.append(f"📝【{article.title}】\n{summary}\n")
        full_log.append(f"検索語: {query} / タイトル: {article.title} / 要約: {summary}")

    # ログ保存
    for line in full_log:
        save_log(line)

    return "\n\n".join(summaries), "\n".join(full_log)


# Gradio インターフェース設定
iface = gr.Interface(
    fn=search_and_summarize,
    inputs=gr.Textbox(label="PubMed 検索キーワード"),
    outputs=[
        gr.Textbox(label="要約結果"),
        gr.Textbox(label="保存されたログ内容")
    ],
    title="PubMed 論文要約アプリ",
    description="キーワードを入力すると、PubMedから論文を取得して要約します。",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()
