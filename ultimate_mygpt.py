from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles  # ここで静的ファイル用モジュールをインポート
import argparse
import os
import datetime
import platform

# FastAPI のインスタンスを作成し、「app」という名前で公開します。
app = FastAPI(
    title="Ultimate MyGPT-Paper Analyzer API",
    description="PubMed/PMC, arXiv, bioRxiv 論文の検索、解析、要約、チャンク化、埋め込み生成を提供するAPI。",
    version="2.0.0"
)

# 静的ファイル（HTML, CSS, JavaScriptなど）を提供するための設定
# ここでは "static" というフォルダからファイルを提供し、URLパスは /static とします。
app.mount("/static", StaticFiles(directory="static"), name="static")

# ルートエンドポイント "/" を定義。アクセスすると "Hello, World!" が返ります。
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# /health エンドポイント（システムの動作確認用）
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}

# /version エンドポイント（バージョン情報を返す）
@app.get("/version")
def version_info():
    version = "2.0.0"
    build_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os_info = platform.platform()
    return {"version": version, "build_time": build_time, "platform": os_info}

# /status エンドポイント（システム状態を返す）
@app.get("/status")
def status_info():
    return {
        "status": "running",
        "uptime": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "base_dir": os.getcwd()
    }

# /ner エンドポイントの定義
@app.get("/ner")
def ner_endpoint(text: str = Query(..., description="解析対象のテキスト")):
    entities = []
    if "Apple" in text:
        entities.append(("Apple", "ORG"))
    return {"entities": entities}

# /summary エンドポイントの定義
@app.get("/summary")
def summary_endpoint(text: str = Query(..., description="要約対象のテキスト")):
    summary = text[:50] + "..." if len(text) > 50 else text
    return {"summary": summary}

# PubMed から論文データを取得し、整形して成果物として保存する関数（本番処理用）
def fetch_and_process():
    print("PubMedから論文を取得し、整形処理を実行中...")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "processed_data.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ここに整形済みの論文データが入ります。")
    print("処理完了。成果物は", output_path, "に保存されました。")

# main 関数：コマンドライン引数で実行モードを切り替えます。
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
    parser.add_argument('--mode', type=str, default='development', help='実行モード (production or development)')
    args = parser.parse_args()
    main(args.mode)
