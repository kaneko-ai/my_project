# gradio_vector_search.py

import gradio as gr
from nlp.vector_router import search_vector

def run_query(query, backend):
    if not query.strip():
        return "⚠️ 検索ワードを入力してください"

    try:
        results = search_vector(query, top_k=5, backend=backend)
        if not results:
            return "🔍 類似論文が見つかりませんでした。"
        
        display = "🧠 類似論文トップ5：\\n"
        for i, item in enumerate(results, 1):
            display += f"\\n{i}. 『{item['title']}』\\n"
            display += f"   📊 類似スコア: {item['score']}\\n"
            display += f"   📄 要約: {item['content'][:150]}...\\n"
        return display
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# Gradio UI構成
with gr.Blocks(title="ベクトル検索 MyGPT") as demo:
    gr.Markdown("# 🔍 類似論文検索（Chroma / FAISS 切替対応）")
    with gr.Row():
        query_input = gr.Textbox(label="検索ワード（自然文）", placeholder="例：肺がん治療の新しいアプローチ")
        backend_choice = gr.Dropdown(choices=["chroma", "faiss"], value="chroma", label="ベクトルDBエンジン")

    output = gr.Textbox(label="検索結果", lines=15)

    search_button = gr.Button("検索する！")
    search_button.click(fn=run_query, inputs=[query_input, backend_choice], outputs=output)

# 実行
if __name__ == "__main__":
    demo.launch()
