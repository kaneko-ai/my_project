# gradio_advanced_search.py

import gradio as gr
from nlp.vector_router import search_vector
import matplotlib.pyplot as plt

# ノイズ除去のしきい値（例: 類似度0.6未満をカット）
SIMILARITY_THRESHOLD = 0.6

# ダミーのキーワード検索（ベクトル検索とUI合わせる用）
def keyword_search(query):
    # TODO: 本格導入時は全文検索 or Elastic導入
    return [{
        "title": "Keyword Match Dummy Result",
        "content": "This is a keyword match example.",
        "score": 0.99,
        "metadata": {}
    }]

# メイン検索関数（複合検索）
def run_query(query, method, backend):
    if not query.strip():
        return "⚠️ 検索ワードを入力してください", None

    if method == "ベクトル検索":
        results = search_vector(query, top_k=10, backend=backend)
    elif method == "キーワード検索":
        results = keyword_search(query)
    else:
        results = []

    # ノイズ除去（A6）
    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]
    if not filtered:
        return "🔍 有効な結果がありませんでした（類似度しきい値で除外された可能性あり）", None

    # 結果テキスト整形
    text_output = "🧠 検索結果（類似スコア ≥ {:.1f}）:\n".format(SIMILARITY_THRESHOLD)
    for i, r in enumerate(filtered, 1):
        text_output += f"\n{i}. 『{r['title']}』\n"
        text_output += f"   📊 類似スコア: {r['score']}\n"
        text_output += f"   📄 要約: {r['content'][:150]}...\n"

    # スコアグラフ（A3）
    fig, ax = plt.subplots()
    titles = [r["title"][:30] for r in filtered]
    scores = [r["score"] for r in filtered]
    ax.barh(titles, scores, color="skyblue")
    ax.set_xlabel("類似度スコア")
    ax.invert_yaxis()
    ax.set_title("📊 類似度スコア比較")
    fig.tight_layout()

    return text_output, fig

# Gradio UI構築
with gr.Blocks(title="MyGPT検索UI（強化版）") as demo:
    gr.Markdown("# 🔍 類似論文検索（ベクトル＋キーワード＋スコアグラフ）")

    with gr.Row():
        query_input = gr.Textbox(label="検索ワード", placeholder="例：免疫療法による肺がん治療")
        method_choice = gr.Radio(["ベクトル検索", "キーワード検索"], value="ベクトル検索", label="検索手法")
        backend_choice = gr.Dropdown(choices=["chroma", "faiss"], value="chroma", label="ベクトルDB")

    search_button = gr.Button("検索する")

    result_box = gr.Textbox(label="検索結果", lines=12)
    graph_plot = gr.Plot(label="類似度グラフ")

    search_button.click(
        fn=run_query,
        inputs=[query_input, method_choice, backend_choice],
        outputs=[result_box, graph_plot]
    )

# 実行
if __name__ == "__main__":
    demo.launch()
