from dotenv import load_dotenv
import os

from fastapi import FastAPI
from routers import pubmed, embed, summary, logs, auth, arxiv_biorxiv  # ← arxiv_biorxiv 追加

# .envファイルから環境変数を読み込む
load_dotenv()

# 読み込んだ環境変数を取得
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

app = FastAPI()

# 各機能のルーターをアプリに登録
app.include_router(pubmed.router)
app.include_router(embed.router)
app.include_router(summary.router)
app.include_router(logs.router)
app.include_router(auth.router)
app.include_router(arxiv_biorxiv.router)  # ← 新たに追加した arxiv/biorxiv のAPIルーター

# トップページのルート定義
@app.get("/")
def root():
    return {
        "message": "ようこそ！MyGPTアナライザーへ",
        "email": EMAIL_ADDRESS,
        "api_key_loaded": NCBI_API_KEY is not None
    }

# 開発用の実行ブロック（ローカル起動用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
