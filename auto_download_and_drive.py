from api_clients.pubmed_client import fetch_pubmed_articles
from api_clients.arxiv_biorxiv_client import fetch_arxiv_articles, fetch_biorxiv_articles
from nlp.summary_model import summarize_text
from utils.model_recommender import recommend_model
from datetime import datetime
from fpdf import FPDF
import io
import os

KEYWORDS = ["GPT", "医療", "LLM"]  # 検索対象
LOCAL_OUTPUT_DIR = "output"  # 保存先ルートディレクトリ（タグごとにサブフォルダを作成）


def generate_summary_pdf(title, model_name, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"タイトル: {title}")
    pdf.multi_cell(0, 10, f"モデル: {model_name}")
    pdf.multi_cell(0, 10, "\n[要約]\n" + summary)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


def save_pdf_locally(filename, pdf_buffer, tag):
    tag_dir = os.path.join(LOCAL_OUTPUT_DIR, tag)
    os.makedirs(tag_dir, exist_ok=True)
    path = os.path.join(tag_dir, filename)
    with open(path, "wb") as f:
        f.write(pdf_buffer.read())


def main():
    print("📄 論文取得＆要約＆PDF生成（ローカル保存）開始...")

    for kw in KEYWORDS:
        print(f"\n🔍 キーワード: {kw}")

        articles = fetch_pubmed_articles(kw) + fetch_arxiv_articles(kw) + fetch_biorxiv_articles(kw)
        if not articles:
            print("❌ 論文なし")
            continue

        for idx, article in enumerate(articles[:3]):
            title = article.title.replace("/", "-")[:50]
            abstract = article.abstract
            recommended_model = recommend_model(abstract)
            summary = summarize_text(abstract, model=recommended_model)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{kw}_{idx+1}_{timestamp}.pdf"

            pdf_buffer = generate_summary_pdf(title, recommended_model, summary)
            save_pdf_locally(filename, pdf_buffer, kw)

            print(f"✅ ローカルにPDF保存（{kw} フォルダ）: {filename}")

    print("\n✅ 全処理完了！（output/ 配下に保存済）")


if __name__ == "__main__":
    main()
