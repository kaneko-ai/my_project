from fastapi import FastAPI, Query
import argparse
import os

# FastAPIのインスタンスを「app」という名前で作成
app = FastAPI()

# ルート（"/"）にアクセスしたときの動作（例としてHello Worldを返す）
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# /ner エンドポイント：ここでは例として入力されたテキストをそのまま返します
@app.get("/ner")
def ner_endpoint(text: str = Query(..., description="解析対象のテキスト")):
    # 本来はここでNER（固有表現抽出）の処理を行いますが、例としてそのまま入力テキストを返します
    return {"ner": f"Processed NER for: {text}"}

# /summary エンドポイント：ここでは例として入力テキストの先頭部分を抜粋して返す処理を実装
@app.get("/summary")
def summary_endpoint(text: str = Query(..., description="要約対象のテキスト")):
    # 本来はここで文章の要約処理を行いますが、例として先頭50文字を返す
    summary = text[:50] + "..." if len(text) > 50 else text
    return {"summary": summary}

# PubMedから論文を取得して整形処理を行う関数（本番用）
def fetch_and_process():
    print("PubMedから論文を取得し、整形処理を実行中...")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "processed_data.txt")
    # 例として固定テキストを出力
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ここに整形済み論文のデータが入ります。")
    print("処理完了。成果物は", output_path, "に保存されました。")

# main関数：モードに応じて処理を切り替える
def main(mode):
    if mode == "production":
        print("【本番モード】処理を開始します。")
        fetch_and_process()
    else:
        print("【開発モード】デバッグ用の処理を実行します。")
        print("Hello, World!")

# 直接実行された場合のエントリーポイント
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PubMed 論文取得＆整形処理")
    parser.add_argument('--mode', type=str, default='development', help='実行モード (production または development)')
    args = parser.parse_args()
    main(args.mode)
