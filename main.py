from dotenv import load_dotenv
import os
from fastapi import FastAPI
from routers import pubmed, embed, summary, logs, auth  # ← logs を含める！

load_dotenv()

NCBI_API_KEY = os.getenv("NCBI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

app = FastAPI()

app.include_router(pubmed.router)
app.include_router(embed.router)
app.include_router(summary.router)
app.include_router(logs.router)  # ✅ ログルーターの追加
app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "message": "ようこそ！MyGPTアナライザーへ",
        "email": EMAIL_ADDRESS,
        "api_key_loaded": NCBI_API_KEY is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# ローカル開発用の起動ブロック
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
