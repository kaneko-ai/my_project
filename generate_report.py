import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

df = pd.read_csv("data/misclassified.csv")

# 集計
counts = df.groupby(["label", "predicted"]).size().unstack().fillna(0)

# グラフ保存
plt.figure(figsize=(8, 6))
counts.plot(kind="bar", stacked=True)
plt.title("誤分類分布")
plt.tight_layout()
plt.savefig("outputs/misclassification_chart.png")
plt.close()

# PDFレポート作成
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=14)
pdf.cell(200, 10, txt="誤分類レポート", ln=True, align="C")
pdf.image("outputs/misclassification_chart.png", x=10, y=30, w=180)
pdf.output("outputs/report.pdf")

print("📄 PDFレポート生成完了（outputs/report.pdf）")
