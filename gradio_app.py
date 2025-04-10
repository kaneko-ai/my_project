import gradio as gr
import csv
from datetime import datetime
from routers.summary import summarize_articles  # ✅ 正しくインポート

def summarize_and_prepare_files(query: str):
    try:
        results = summarize_articles(query)  # ✅ ここを修正！

        # テキスト整形（Gradio表示用）
        summary_texts = [
            f"【タイトル】: {r['title']}\n【要約】: {r['summary']}" for r in results
        ]
        joined_text = "\n\n".join(summary_texts)

        # 保存用ファイル名（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        txt_path = f"outputs/summary_{timestamp}.txt"
        csv_path = f"outputs/summary_{timestamp}.csv"

        # 📄 TXT ファイル保存
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(joined_text)

        # 📊 CSV ファイル保存
        with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Summary"])
            for r in results:
                writer.writerow([r["title"], r["summary"]])

        return joined_text, txt_path, csv_path

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None, None

# Gradio UI 構築
iface = gr.Interface(
    fn=summarize_and_prepare_files,
    inputs=gr.Textbox(label="PubMed検索クエリ（例：cancer）"),
    outputs=[
        gr.Textbox(label="論文要約結果", lines=15),
        gr.File(label="TXTファイルダウンロード"),
        gr.File(label="CSVファイルダウンロード"),
    ],
    title="PubMed論文要約ツール (MyGPT)",
    description="キーワードを入力すると、PubMedから論文を取得し要約します。保存もできます。",
)


if __name__ == "__main__":
    import os
    os.makedirs("outputs", exist_ok=True)
    iface.launch()
