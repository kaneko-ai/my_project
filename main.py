from dotenv import load_dotenv
import os
from fastapi import FastAPI
from routers import pubmed, embed, summary, logs, auth

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数の取得
NCBI_API_KEY: str | None = os.getenv("NCBI_API_KEY")
EMAIL_ADDRESS: str | None = os.getenv("EMAIL_ADDRESS")

# FastAPIアプリ生成
app: FastAPI = FastAPI(
    title="MyGPTアナライザー",
    description="論文検索・要約APIサービス",
    version="1.0.0"
)

# 各ルーターを統合（機能別に分割されたAPI）
app.include_router(pubmed.router)
app.include_router(embed.router)
app.include_router(summary.router)
app.include_router(logs.router)
app.include_router(auth.router)

# トップページ
@app.get("/", tags=["Root"])
def root() -> dict[str, str | bool]:
    return {
        "message": "ようこそ！MyGPTアナライザーへ",
        "email": EMAIL_ADDRESS or "未設定",
        "api_key_loaded": NCBI_API_KEY is not None
    }

# ローカル開発用の起動ブロック
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
