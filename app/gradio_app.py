import gradio as gr
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import json, os

# ✅ 要約モデル（複数選択可能）
summarizers = {
    "BART": pipeline("summarization", model="facebook/bart-large-cnn"),
    "Pegasus": pipeline("summarization", model="google/pegasus-xsum"),
    "Flan-T5": pipeline("summarization", model="google/flan-t5-large", tokenizer="google/flan-t5-large")
}

# ✅ 埋め込み用モデル（文類似検索用）
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ ローカルDB（JSONL）から読み込み
def load_summary_db(filepath="db/summary_db.jsonl"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return [json.loads(line) for line in f]

# ✅ 類似検索（top-k）
def search_similar(query, db, top_k=3):
    query_vec = embedder.encode(query, convert_to_tensor=True)
    texts = [item["summary"] for item in db]
    text_vecs = embedder.encode(texts, convert_to_tensor=True)
    scores = util.cos_sim(query_vec, text_vecs)[0]
    top_results = sorted(zip(scores, db), key=lambda x: x[0], reverse=True)[:top_k]
    return [(float(score), item["summary"]) for score, item in top_results]

# ✅ Gradioインターフェース
def process_input(input_text, model_choice, task):
    if task == "要約":
        # Flan-T5には明示的なprefixが必要
        if model_choice == "Flan-T5":
            input_text = "summarize: " + input_text

        summary = summarizers[model_choice](
            input_text,
            max_length=300,
            min_length=50,
            do_sample=False
        )[0]["summary_text"]
        return summary

    elif task == "類似要約検索":
        db = load_summary_db()
        results = search_similar(input_text, db)
        return "\n\n".join([f"スコア:{s:.2f}\n{summ}" for s, summ in results])

    else:
        return "未実装のタスクです"

demo = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(label="入力テキスト"),
        gr.Radio(["BART", "Pegasus", "Flan-T5"], label="要約モデル"),
        gr.Radio(["要約", "類似要約検索"], label="処理タスク")
    ],
    outputs="text"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
