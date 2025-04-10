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

# カテゴリ分類（ルールベース）
def classify_category(text: str):
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text.lower() for k in keywords):
            return category
    return "その他"

# 類似度しきい値
SIMILARITY_THRESHOLD = 0.6

# ダミーのキーワード検索（A2用）
def keyword_search(query):
    return [{
        "title": "Keyword Match Dummy Result",
        "content": "This is a keyword match example.",
        "score": 0.99,
        "metadata": {}
    }]

# 🔍 メイン検索処理（A2/A3/A6/B2/B3対応）
def run_query(query, method, backend):
    if not query.strip():
        return "⚠️ 検索ワードを入力してください", None

    if method == "ベクトル検索":
        results = search_vector(query, top_k=10, backend=backend)
    else:
        results = keyword_search(query)

    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]
    if not filtered:
        return "🔍 有効な結果がありませんでした（スコアしきい値で除外）", None

    text_output = f"🧠 検索結果（スコア ≥ {SIMILARITY_THRESHOLD:.1f}）:\n"
    for i, r in enumerate(filtered, 1):
        tag = classify_category(r['content'])
        rewritten = rewrite_summary(r['content'])
        text_output += f"\n{i}. 『{r['title']}』 [{tag}]\n"
        text_output += f"   📊 類似スコア: {r['score']}\n"
        text_output += f"   {rewritten}\n"

    # 📊 グラフ（A3）
    fig, ax = plt.subplots()
    titles = [r["title"][:30] for r in filtered]
    scores = [r["score"] for r in filtered]
    ax.barh(titles, scores, color="skyblue")
    ax.set_xlabel("類似度スコア")
    ax.invert_yaxis()
    ax.set_title("📊 類似度スコア比較")
    fig.tight_layout()

    return text_output, fig

# 💬 C2: 質問 → 回答（テンプレート構成）
def ask_question_simple(question, backend):
    if not question.strip():
        return "⚠️ 質問を入力してください"

    results = search_vector(question, top_k=5, backend=backend)
    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]

    if not filtered:
        return "💬 該当情報が見つかりませんでした。"

    context = "\n".join([f"- {r['title']}: {r['content'][:100]}..." for r in filtered])

    answer = f"""
🧠【自動生成された参考回答】

「{question}」に関して、以下の研究が関連しています：

{context}

これらの研究に共通しているのは「{question[:10]}」がキーワードである点です。
"""
    return answer.strip()

# 🧪 C3: 自動スコアで要約比較
def evaluate_summaries_simple(text):
    summaries = {
        "Flan-T5": text[:100] + " [flan]",
        "Pegasus": text[:100] + " [peg]",
        "BART": text[:100] + " [bart]"
    }

    def score(summary):
        length = len(summary)
        keywords = sum(1 for kw in ["cancer", "therapy", "risk", "patient"] if kw in summary.lower())
        return round(5 - abs(150 - length) / 30 + keywords, 2)

    result = "🧪 自動評価スコア（目安）:\n"
    for name, s in summaries.items():
        result += f"- {name}: スコア {score(s)} / 10\n"
    return result

# ✅ Gradio UI定義
with gr.Blocks(title="MyGPT 拡張無料UI") as demo:
    gr.Markdown("# 🔍 MyGPT 無料版：検索＋質問＋評価")

    # 🔍 検索エリア（A2〜A6, B2, B3）
    with gr.Row():
        query_input = gr.Textbox(label="検索ワード", placeholder="例：免疫療法 肺がん")
        method_choice = gr.Radio(["ベクトル検索", "キーワード検索"], value="ベクトル検索", label="検索方式")
        backend_choice = gr.Dropdown(["chroma", "faiss"], value="chroma", label="ベクトルDB")

    run_btn = gr.Button("検索する")
    result_text = gr.Textbox(label="検索結果", lines=14)
    score_graph = gr.Plot(label="📊 類似スコア可視化")
    run_btn.click(fn=run_query, inputs=[query_input, method_choice, backend_choice], outputs=[result_text, score_graph])

    # 💬 C2: 質問 → 回答
    gr.Markdown("## 💬 自然文で質問して検索（GPTなし）")
    with gr.Row():
        q_input = gr.Textbox(label="質問（例：肺がんの新しい治療法は？）")
        q_backend = gr.Dropdown(["chroma", "faiss"], value="chroma", label="ベクトルDB")
    q_output = gr.Textbox(label="参考回答（テンプレ生成）", lines=5)
    gr.Button("質問する").click(fn=ask_question_simple, inputs=[q_input, q_backend], outputs=q_output)

    # 🧪 C3: 要約比較
    gr.Markdown("## 🧪 要約の自動スコア比較（無料版）")
    s_input = gr.Textbox(label="評価したい元テキスト", lines=4)
    s_output = gr.Textbox(label="スコア結果", lines=6)
    gr.Button("要約を比較評価する").click(fn=evaluate_summaries_simple, inputs=s_input, outputs=s_output)

# 🚀 起動
if __name__ == "__main__":
    demo.launch()
