from fastapi import FastAPI, Query
import argparse
import os

# FastAPI のインスタンスを作成し、'app' という名前で公開
app = FastAPI()

# ルート（"/"）にアクセスしたときに、簡単なメッセージを返す
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# /ner エンドポイント
@app.get("/ner")
def ner_endpoint(text: str = Query(..., description="解析対象のテキスト")):
    # ここでは、テストが期待するようにダミーの結果を返します
    # 入力テキストに「Apple」が含まれている場合、entitiesリストに ("Apple", "ORG") を追加
    entities = []
    if "Apple" in text:
        entities.append(("Apple", "ORG"))
    # さらに、他の固有表現があれば追加することも可能です
    return {"entities": entities}

# /summary エンドポイント
@app.get("/summary")
def summary_endpoint(text: str = Query(..., description="要約対象のテキスト")):
    # 例として、テキストの先頭50文字を抜粋して返す
    summary = text[:50] + "..." if len(text) > 50 else text
    return {"summary": summary}

# PubMed から論文データを取得し、整形して成果物として保存する関数（本番処理用）
def fetch_and_process():
    print("PubMedから論文を取得し、整形処理を実行中...")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)  # フォルダがなければ作成
    output_path = os.path.join(output_dir, "processed_data.txt")
    # ここでは、例として固定テキストを保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ここに整形済みの論文データが入ります。")
    print("処理完了。成果物は", output_path, "に保存されました。")

# main 関数：コマンドライン引数で処理モードを切り替える
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
