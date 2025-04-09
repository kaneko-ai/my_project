from fastapi import FastAPI
from routers import pubmed, embed, summary, logs, auth

app = FastAPI()

# 機能を全部つなげる
app.include_router(pubmed.router)
app.include_router(embed.router)
app.include_router(summary.router)
app.include_router(logs.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "ようこそ！MyGPTアナライザーへ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
