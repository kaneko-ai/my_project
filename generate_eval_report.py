from fpdf import FPDF
from datetime import datetime
from sklearn.metrics import classification_report
import pandas as pd
import pickle

# モデルと評価対象を読み込み
model_path = "models/structure_label_model_retrained.pkl"
df = pd.read_csv("data/training_data_latest.csv")
X = df["summary"]
y = df["label"]

with open(model_path, "rb") as f:
    model = pickle.load(f)

y_pred = model.predict(X)
report_str = classification_report(y, y_pred)

# PDFレポート作成
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="モデル評価レポート", ln=True, align="C")
pdf.multi_cell(0, 10, report_str)
pdf.output("data/eval_report.pdf")

print("✅ PDF出力完了: data/eval_report.pdf")
