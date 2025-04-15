from fpdf import FPDF
from typing import List
from models.article_summary import ArticleSummary
import os

# IPAフォントファイルのパス（プロジェクト直下に fonts/ipaexg.ttf を置いておくと仮定）
FONT_PATH = os.path.join("fonts", "ipaexg.ttf")

def save_summaries_as_pdf(summaries: List[ArticleSummary], output_path: str = "summaries.pdf"):
    pdf = FPDF()
    pdf.add_page()

    # 日本語対応フォントの追加（TrueTypeフォント）
    pdf.add_font("IPA", "", FONT_PATH, uni=True)
    pdf.set_font("IPA", size=12)

    for summary in summaries:
        pdf.multi_cell(0, 10, f"【タイトル】{summary.title}")
        pdf.multi_cell(0, 10, f"【著者】{', '.join(summary.authors) if summary.authors else '不明'}")
        pdf.multi_cell(0, 10, f"【ジャーナル】{summary.journal or '不明'}")
        pdf.multi_cell(0, 10, f"【発行年】{summary.year or '不明'}")
        pdf.multi_cell(0, 10, f"【要旨】{summary.abstract or 'なし'}")
        pdf.multi_cell(0, 10, f"【引用】{summary.citation or 'なし'}")
        pdf.cell(0, 10, "────────────────────────────", ln=True)

    pdf.output(output_path)
    print(f"✅ {output_path} にPDFとして保存しました。")
