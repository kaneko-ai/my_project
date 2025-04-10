import gradio as gr
import csv
import os
from datetime import datetime
from routers.summary import summarize_articles  # あなたの要約処理（API経由）
from utils.translation import translate_to_japanese
from utils.summary_advanced import summarize_advanced, extract_key_sentences, classify_tags
from utils.medical_terms import annotate_medical_terms
from utils.qna_generator import generate_qna

os.makedirs("outputs", exist_ok=True)
seen_titles = set()

def summarize_and_prepare_files(query: str, qa_mode: bool):
    try:
        articles = summarize_articles(query)
        if not articles:
            return "論文が見つかりませんでした。", None, None

        summary_texts = []
        csv_rows = []

        for article in articles:
            if article.title in seen_titles:
                continue  # 重複排除
            seen_titles.add(article.title)

            # 要約生成（精度高め）
            raw_summary = summarize_advanced(article.abstract)
            ja_summary = translate_to_japanese(raw_summary)
            key_sents = extract_key_sentences(article.abstract)
            tags = classify_tags(article.abstract)

            # 医学用語の注釈を追加
            tooltip_title = annotate_medical_terms(article.title)
            tooltip_summary = annotate_medical_terms(ja_summary)

            # Q&A生成
            qa_pairs = generate_qna(article.abstract) if qa_mode else []

            # テキスト形式でまとめ
            text_block = f"【タイトル】: {tooltip_title}\n"
            text_block += f"【要約】: {tooltip_summary}\n"
            text_block += f"【重要文】: {' / '.join(key_sents)}\n"
            text_block += f"【タグ】: {'・'.join(tags)}\n"
            if qa_mode:
                text_block += "【Q&Aモード】:\n"
                for q, a in qa_pairs:
                    text_block += f"Q: {q}\nA: {a}\n"
            summary_texts.append(text_block)

            csv_rows.append([
                article.title,
                raw_summary,
                ja_summary,
                " / ".join(key_sents),
                ", ".join(tags)
            ])

        joined_text = "\n\n".join(summary_texts)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        txt_path = f"outputs/summary_{timestamp}.txt"
        csv_path = f"outputs/summary_{timestamp}.csv"

        # TXT保存
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(joined_text)

        # CSV保存
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Summary_en", "Summary_ja", "Key Sentences", "Tags"])
            writer.writerows(csv_rows)

        return joined_text, txt_path, csv_path

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None, None


# Gradio UI 設定
iface = gr.Interface(
    fn=summarize_and_prepare_files,
    inputs=[
        gr.Textbox(label="PubMed検索クエリ（例：cancer）"),
        gr.Checkbox(label="ChatGPT風Q&Aモード")
    ],
    outputs=[
        gr.Textbox(label="論文要約結果", lines=20),
        gr.File(label="TXTファイルダウンロード"),
        gr.File(label="CSVファイルダウンロード"),
    ],
    title="PubMed論文要約ツール (MyGPT)",
    description="キーワードを入力すると、PubMedから論文を取得し、重要文抽出・日本語翻訳・タグ分類・Q&A生成まで行います。",
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=8080, share=True)
