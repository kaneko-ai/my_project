import gradio as gr
import os
from tools.db import load_all_papers, search_similar_papers, save_paper, search_by_tag
from tools.paper_processor import vectorize_text, process_paper
from tools.pdf_handler import extract_text_from_pdf, summarize_text
from tools.auto_tagging import auto_detect_tags

def show_all_papers():
    data = []
    for paper in load_all_papers():
        data.append({
            "タイトル": paper["title"],
            "要旨": paper["abstract"][:200] + "...",
            "スコア": paper["score"],
            "タグ": ", ".join(paper.get("tags", []))
        })
    return sorted(data, key=lambda x: x["スコア"], reverse=True)

def find_similar(query_text):
    q_vec = vectorize_text(query_text)
    similar = search_similar_papers(q_vec, top_k=5)
    return [
        {
            "タイトル": s["title"],
            "要旨": s["summary"][:200] + "...",
            "スコア": s["score"],
            "類似度": round(s["similarity"], 3),
            "タグ": ", ".join(s.get("tags", []))
        } for s in similar
    ]

def search_by_tag_ui(tag_text):
    results = search_by_tag(tag_text, top_k=5)
    return [
        {
            "タイトル": p["title"],
            "要旨": p["abstract"][:200] + "...",
            "スコア": p["score"],
            "タグ": ", ".join(p.get("tags", []))
        } for p in results
    ]

def register_paper(title, abstract, year, citations, journal_score, tags_input):
    try:
        metadata = {
            "year": year,
            "citations": citations,
            "journal_score": journal_score
        }
        manual_tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        auto_tags = auto_detect_tags(abstract)
        all_tags = list(set(manual_tags + auto_tags))
        result = process_paper(title, abstract, metadata)
        result["tags"] = all_tags
        save_paper(result)
        return f"✅ 登録完了！スコア: {result['score']} タグ: {', '.join(all_tags)}"
    except Exception as e:
        return f"❌ エラー: {e}"

def register_from_pdf(pdf_file, year, citations, journal_score, tags_input):
    try:
        text = extract_text_from_pdf(pdf_file.name)
        summary = summarize_text(text)
        title = os.path.splitext(os.path.basename(pdf_file.name))[0]
        metadata = {
            "year": year,
            "citations": citations,
            "journal_score": journal_score
        }
        manual_tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        auto_tags = auto_detect_tags(summary)
        all_tags = list(set(manual_tags + auto_tags))
        result = process_paper(title, summary, metadata)
        result["tags"] = all_tags
        save_paper(result)
        return f"✅ PDF登録完了！スコア: {result['score']} タグ: {', '.join(all_tags)}"
    except Exception as e:
        return f"❌ エラー: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# 📘 論文DBビューア＆類似検索＆登録")

    with gr.Tab("📚 閲覧＆検索"):
        with gr.Row():
            query_input = gr.Textbox(label="🔍 検索キーワード")
            search_button = gr.Button("類似検索")

        similar_output = gr.Dataframe(headers=["タイトル", "要旨", "スコア", "類似度", "タグ"], row_count=5)
        search_button.click(fn=find_similar, inputs=query_input, outputs=similar_output)

        gr.Markdown("## 📚 保存された論文一覧")
        paper_list = gr.Dataframe(headers=["タイトル", "要旨", "スコア", "タグ"], row_count=10)
        demo.load(fn=show_all_papers, inputs=None, outputs=paper_list)

        gr.Markdown("## 🔍 タグで絞り込み検索")
        tag_input = gr.Textbox(label="タグ名（例：LLM）")
        tag_search_btn = gr.Button("検索")
        tag_output = gr.Dataframe(headers=["タイトル", "要旨", "スコア", "タグ"], row_count=5)
        tag_search_btn.click(fn=search_by_tag_ui, inputs=tag_input, outputs=tag_output)

    with gr.Tab("📥 論文登録"):
        gr.Markdown("### 任意の論文を登録する")

        input_title = gr.Textbox(label="タイトル")
        input_abstract = gr.Textbox(label="要旨", lines=4)
        with gr.Row():
            input_year = gr.Textbox(label="発表年", placeholder="例：2023")
            input_citations = gr.Textbox(label="引用数", placeholder="例：123")
            input_journal_score = gr.Textbox(label="ジャーナル評価 (0〜1)", placeholder="例：0.8")
        input_tags = gr.Textbox(label="タグ（カンマ区切り）", placeholder="例: LLM, 医療, GPT")

        register_btn = gr.Button("登録")
        register_output = gr.Textbox(label="ステータス")

        register_btn.click(
            fn=register_paper,
            inputs=[input_title, input_abstract, input_year, input_citations, input_journal_score, input_tags],
            outputs=register_output
        )

    with gr.Tab("📄 PDFから登録"):
        gr.Markdown("### PDFをアップロードして要約＆登録")

        pdf_input = gr.File(label="PDFアップロード", type="file")
        with gr.Row():
            pdf_year = gr.Textbox(label="発表年", placeholder="例：2023")
            pdf_citations = gr.Textbox(label="引用数", placeholder="例：456")
            pdf_journal_score = gr.Textbox(label="ジャーナル評価", placeholder="例：0.9")
        pdf_tags = gr.Textbox(label="タグ（カンマ区切り）", placeholder="例: LLM, 医療, GPT")

        pdf_register_btn = gr.Button("PDFから登録する！")
        pdf_register_output = gr.Textbox(label="ステータス")

        pdf_register_btn.click(
            fn=register_from_pdf,
            inputs=[pdf_input, pdf_year, pdf_citations, pdf_journal_score, pdf_tags],
            outputs=pdf_register_output
        )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)  # ✅ 外部アクセス可能にするための変更点
