# --- ai_pipeline_manager.py ---
# 論文要約・分類・評価のフルパイプラインを一括実行
from summarize_and_store import process_paper
from classify_field_bert import classify_field
from utils.evaluator import evaluate_paper
import os
import json

def full_pipeline(input_folder):
    print(f"📂 フォルダ内のPDFを処理します: {input_folder}")
    for file in os.listdir(input_folder):
        if file.endswith(".pdf"):
            paper_path = os.path.join(input_folder, file)
            print(f"\n--- 論文: {file} ---")
            result = process_paper(paper_path)
            field, score = classify_field(result["title"], result["summary"])
            result["field"] = field
            result["field_score"] = score
            eval_scores = evaluate_paper(result)
            result.update(eval_scores)
            print(f"✅ 結果保存済み: {result['doi'] if 'doi' in result else 'N/A'}")

if __name__ == "__main__":
    full_pipeline("papers")

