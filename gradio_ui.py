import gradio as gr
from routers.summary import summarize_articles_from_pubmed_query

def summarize_from_ui(query: str):
    try:
        results = summarize_articles_from_pubmed_query(query)
        texts = [f"【タイトル】: {r['title']}\n【要約】: {r['summary']}" for r in results]
        return "\n\n".join(texts)
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

iface = gr.Interface(
    fn=summarize_from_ui,
    inputs=gr.Textbox(label="PubMed検索クエリ（例：cancer）"),
    outputs=gr.Textbox(label="論文要約結果", lines=15),
    title="PubMed論文要約ツール (MyGPT)",
    description="キーワードを入力すると、PubMedから論文を取得し要約します。"
)

if __name__ == "__main__":
    iface.launch()
