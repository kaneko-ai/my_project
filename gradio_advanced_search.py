import gradio as gr
import matplotlib.pyplot as plt
import json
import datetime
import os
import pdfplumber

from transformers import pipeline
from nlp.vector_router import search_vector

# ======================
# 🔧 モデル準備（Flan, Pegasus, BART）
# ======================
summarizer_flan = pipeline("summarization", model="google/flan-t5-base")
summarizer_pegasus = pipeline("summarization", model="google/pegasus-xsum")
summarizer_bart = pipeline("summarization", model="facebook/bart-large-cnn")

# ======================
# 💡 疾患カテゴリ分類（B3）
# ======================
CATEGORY_KEYWORDS = {
    "がん系": ["cancer", "tumor", "oncology"],
    "神経系": ["brain", "neuro", "alzheim", "parkinson"],
    "代謝系": ["diabetes", "insulin", "glucose", "metabolism"],
    "循環器系": ["heart", "cardio", "vascular", "stroke"],
}

def classify_category(text: str):
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text.lower() for k in keywords):
            return category
    return "その他"

def rewrite_summary(summary: str):
    return f"💬 要約：この研究では、{summary[:60]}... と報告されています。"
# ======================
# 共通設定
# ======================
SIMILARITY_THRESHOLD = 0.6
DB_PATH = "summary_db.jsonl"  # 要約保存先（B4）

# ======================
# 🔍 検索（A2〜A6, B2, B3）
# ======================
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
    else:
        results = keyword_search(query)

    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]
    if not filtered:
        return "🔍 有効な結果がありませんでした", None

    text_output = f"🧠 類似文書（スコア ≥ {SIMILARITY_THRESHOLD}）:\n"
    for i, r in enumerate(filtered, 1):
        tag = classify_category(r['content'])
        rewritten = rewrite_summary(r['content'])
        text_output += f"\n{i}. 『{r['title']}』 [{tag}]\n"
        text_output += f"   📊 スコア: {r['score']}\n"
        text_output += f"   {rewritten}\n"

    fig, ax = plt.subplots()
    titles = [r["title"][:30] for r in filtered]
    scores = [r["score"] for r in filtered]
    ax.barh(titles, scores, color="skyblue")
    ax.set_xlabel("類似度スコア")
    ax.invert_yaxis()
    ax.set_title("📊 類似スコア")
    fig.tight_layout()

    return text_output, fig

# ======================
# 💬 C2: 質問→自動テンプレ回答
# ======================
def ask_question_simple(question, backend):
    results = search_vector(question, top_k=5, backend=backend)
    filtered = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]
    if not filtered:
        return "該当情報なし"

    context = "\n".join([f"- {r['title']}: {r['content'][:100]}..." for r in filtered])
    return f"🧠 質問: {question}\n関連研究:\n{context}"

# ======================
# 🧪 C3: 3モデル実要約＆比較
# ======================
def compare_summaries(text):
    sum_flan = summarizer_flan(text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
    sum_peg = summarizer_pegasus(text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
    sum_bart = summarizer_bart(text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]

    return f"【Flan-T5】\n{sum_flan}\n\n【Pegasus】\n{sum_peg}\n\n【BART】\n{sum_bart}"

# ======================
# 🧾 B4: 要約保存
# ======================
def save_summary(title, content, summary):
    data = {
        "title": title,
        "content": content,
        "summary": summary,
        "category": classify_category(content),
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(DB_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    return "✅ 要約を保存しました"

# ======================
# 📄 PDFアップロード → 要約
# ======================
def summarize_pdf(file):
    with pdfplumber.open(file.name) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    summary = summarizer_pegasus(text[:2000], max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
    return summary
# ======================
# Gradio UI 統合
# ======================

with gr.Blocks(title="MyGPT 無料強化UI") as demo:
    gr.Markdown("# 🔍 MyGPT 無料統合UI：検索 / 質問 / 要約比較 / PDF / DB保存")

    # 🔍 検索エリア
    gr.Markdown("## 🔍 類似文献検索")
    with gr.Row():
        query_input = gr.Textbox(label="検索クエリ", placeholder="例: 免疫療法 肺がん")
        method_choice = gr.Radio(["ベクトル検索", "キーワード検索"], value="ベクトル検索", label="検索方式")
        backend_choice = gr.Dropdown(["chroma", "faiss"], value="chroma", label="ベクトルDB")

    run_btn = gr.Button("検索実行")
    result_text = gr.Textbox(label="検索結果", lines=12)
    score_graph = gr.Plot(label="📊 類似度グラフ")
    run_btn.click(fn=run_query, inputs=[query_input, method_choice, backend_choice], outputs=[result_text, score_graph])

    # 💬 質問 → テンプレ回答
    gr.Markdown("## 💬 自然文で質問（例：肺がんの治療法は？）")
    with gr.Row():
        q_input = gr.Textbox(label="質問内容")
        q_backend = gr.Dropdown(["chroma", "faiss"], value="chroma", label="検索対象")
    q_output = gr.Textbox(label="参考回答", lines=6)
    gr.Button("質問する").click(fn=ask_question_simple, inputs=[q_input, q_backend], outputs=q_output)

    # 🧪 要約比較（実モデル）
    gr.Markdown("## 🧪 3モデルによる要約比較（Flan-T5 / Pegasus / BART）")
    s_input = gr.Textbox(label="要約対象テキスト", lines=5)
    s_output = gr.Textbox(label="要約結果", lines=10)
    gr.Button("比較する").click(fn=compare_summaries, inputs=s_input, outputs=s_output)

    # 📤 PDFアップロード → 自動要約
    gr.Markdown("## 📄 PDFから全文読み込み＆要約")
    pdf_input = gr.File(label="PDFファイルを選択")
    pdf_output = gr.Textbox(label="要約結果", lines=6)
    gr.Button("PDFを要約").click(fn=summarize_pdf, inputs=pdf_input, outputs=pdf_output)

    # 💾 要約保存（B4）
    gr.Markdown("## 💾 要約データベース保存")
    with gr.Row():
        save_title = gr.Textbox(label="タイトル")
        save_text = gr.Textbox(label="本文（または要約元）")
        save_summary_text = gr.Textbox(label="要約")
    save_output = gr.Textbox(label="保存結果")
    gr.Button("要約を保存").click(fn=save_summary, inputs=[save_title, save_text, save_summary_text], outputs=save_output)

# ✅ 実行
if __name__ == "__main__":
    demo.launch()
