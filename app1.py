# app.py

from fastapi import FastAPI
import spacy

app = FastAPI()
nlp = spacy.load("en_core_web_sm")

@app.get("/ner")
def ner_endpoint(text: str):
    """テキストを受け取って固有表現を抽出し、結果を返す。"""
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return {"entities": entities}
