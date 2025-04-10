# gradio_advanced_search.py

import gradio as gr
import matplotlib.pyplot as plt
from nlp.vector_router import search_vector

# 💡 疾患カテゴリ分類ルール（簡易ルールベース）
CATEGORY_KEYWORDS = {
    "がん系": ["cancer", "tumor", "oncology"],
    "神経系": ["brain", "neuro", "alzheim", "parkinson"],
    "代謝系": ["diabetes", "insulin", "glucose", "metabolism"],
    "循環器系": ["heart", "cardio", "vascular", "stroke"],
}

# 🤖 簡易リライト関数（GPT風整形）
def rewrite_summary(summary: str):
    return f"💬 要約：この研究では、{summary[:60]}... と報告されています。"

# 🧠 カテゴリ分類（B3）
def classify_category(text: str):
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text.lower() for k in keywords):
            return category
    return "その他"

# 🧠 検索関数（ベクトル or キーワード）
SIMILARITY_THRESHOLD = 0.6

def keyword_search(query):
    return [{
        "title": "Keyword Match Dummy",
        "content": "This is a mock keyword result.",
        "score": 0.98,
        "metadata": {}
    }]

def run_query(query, method, backend):
    if not query.strip():
        return "⚠️ 検索ワードを入力してください", None

    if method == "ベクトル検索":
        results = search_vector(query, top_k=10, backend=backend)
    elif method == "キーワード検索":
        results = keyword_search(query)
    else:
        results = []

    # フィルタ処理（A6）
    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]
    if not filtered:
        return "🔍 有効な結果がありませんでした（スコアが低い可能性）", None

    # テキスト整形：要約＋カテゴリ＋リライト（B2, B3）
    text_output = f"🧠 検索結果（スコア ≥ {SIMILARITY_THRESHOLD:.1f}）:\n"
    for i, r in enumerate(filtered, 1):
        tag = classify_category(r['content'])
        rewritten = rewrite_summary(r['content'])
        text_output += f"\n{i}. 『{r['title']}』 [{tag}]\n"
        text_output += f"   📊 類似スコア: {r['score']}\n"
        text_output += f"   {rewritten}\n"

    # グラフ（A3）
    fig, ax = plt.subplots()
    titles = [r["title"][:30] for r in filtered]
    scores = [r["score"] for r in filtered]
    ax.barh(titles, scores, color="skyblue")
    ax.set_xlabel("類似度スコア")
    ax.invert_yaxis()
    ax.set_title("📊 類似度スコア比較")
    fig.tight_layout()

    return text_output, fig

# Gradio UI
with gr.Blocks(title="MyGPT拡張検索UI") as demo:
    gr.Markdown("# 🔍 論文検索：ベクトル＋キーワード＋リライト＋分類")

    with gr.Row():
        query_input = gr.Textbox(label="検索ワード", placeholder="例：免疫療法 肺がん")
        method_choice = gr.Radio(["ベクトル検索", "キーワード検索"], value="ベクトル検索", label="検索方式")
        backend_choice = gr.Dropdown(["chroma", "faiss"], value="chroma", label="ベクトルDB")

    run_btn = gr.Button("検索する")
    result_text = gr.Textbox(label="検索結果", lines=14)
    score_graph = gr.Plot(label="類似スコア可視化")

    run_btn.click(
        fn=run_query,
        inputs=[query_input, method_choice, backend_choice],
        outputs=[result_text, score_graph]
    )

if __name__ == "__main__":
    demo.launch()
