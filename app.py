# app.py

import argparse
import os
from fastapi import FastAPI

# ここで FastAPI のインスタンスを作り、「app」という名前で公開します。
# これにより、テストファイルから「from app import app」が動作します。
app = FastAPI()

# 例として、ルートURLにアクセスすると "Hello, World!" を返す設定です。
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# PubMedから論文を取得して整形処理を行う関数
def fetch_and_process():
    print("PubMedから論文を取得し、整形処理を実行中...")
    
    # 成果物（結果のファイル）を保存するためのディレクトリ「output」を作成
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 成果物を「processed_data.txt」という名前で保存
    output_path = os.path.join(output_dir, "processed_data.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ここに整形済みの論文データが入ります。")
    
    print("処理完了。成果物は", output_path, "に保存されました。")

# main関数：実行モードによって処理を切り替えます
def main(mode):
    if mode == "production":
        print("【本番モード】処理を開始します。")
        fetch_and_process()
    else:
        print("【開発モード】デバッグ用の処理を実行します。")
        # 簡単な動作確認のためのメッセージ
        print("Hello, World!")

# このファイルが直接実行された場合の処理
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PubMed 論文取得＆整形処理")
    parser.add_argument('--mode', type=str, default='development', help='実行モード (productionまたはdevelopment)')
    args = parser.parse_args()
    main(args.mode)
