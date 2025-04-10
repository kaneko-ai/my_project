import gradio as gr
import csv
from datetime import datetime
import os
from routers.summary import summarize_articles  # クラスベースで返す関数

def summarize_and_prepare_files(query: str):
    try:
        # 要約結果（ArticleSummary オブジェクトのリスト）
        results = summarize_articles(query)

        # Gradio 表示用の文字列整形（オブジェクト属性としてアクセス）
        summary_texts = [
            f"【タイトル】: {r.title}\n【要約】: {r.summary}" for r in results
        ]
        joined_text = "\n\n".join(summary_texts)

        # 出力ファイルの保存先と名前（タイムスタンプでユニーク化）
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        txt_path = f"outputs/summary_{timestamp}.txt"
        csv_path = f"outputs/summary_{timestamp}.csv"

        # 📄 テキストファイル出力
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(joined_text)

        # 📊 CSVファイル出力
        with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Title", "Summary"])
            for r in results:
                writer.writerow([r.title, r.summary])

        return joined_text, txt_path, csv_path

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None, None


# 🌐 Gradio インターフェース
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

# 🔽 アプリ起動（外部アクセス対応）
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=8080, share=True)
