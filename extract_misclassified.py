import json
import csv
from train_label_classifier import load_model

model = load_model()

with open("data/test_data.json", encoding="utf-8") as f:
    test_data = json.load(f)

misclassified = []
for d in test_data:
    pred = model.predict([d["summary"]])[0]
    if pred != d["label"]:
        d["predicted"] = pred
        misclassified.append(d)

print(f"誤分類数: {len(misclassified)} 件")

with open("data/misclassified.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "summary", "label", "predicted"])
    writer.writeheader()
    writer.writerows(misclassified)
