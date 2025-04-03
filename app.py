# app.py
from fastapi import FastAPI, HTTPException
import spacy

# FastAPI サーバーを作成
app = FastAPI(
    title="Ultimate MyGPT-Paper Analyzer API",
    version="2.0.0"
)

# spacy のモデルをロード
nlp = spacy.load("en_core_web_sm")

@app.get("/ner")
def ner_endpoint(text: str):
    """
    URL のパラメータ 'text' に文章を入れると、その中の固有表現を抽出して返します。
    例: /ner?text=Apple+is+buying+U.K.+startup+for+$1+billion
    """
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return {"entities": entities}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
