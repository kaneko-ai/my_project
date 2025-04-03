# app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn

# 他モジュールから必要な関数やクラスをインポート
from nlp.text_processing import load_spacy_model, summarize_text
from api_clients.pubmed_client import PubMedClient

# FastAPI アプリケーションの作成
app = FastAPI(
    title="Ultimate MyGPT-Paper Analyzer API",
    description="PubMed/PMC, arXiv, bioRxiv 論文の検索、解析、要約、チャンク化、埋め込み生成を提供するAPI",
    version="2.0.0"
)

# 例として、spaCy を使った固有表現抽出のエンドポイント
nlp_model = load_spacy_model()

@app.get("/ner", tags=["NER"])
def ner_endpoint(text: str):
    """入力テキストから固有表現を抽出します。"""
    doc = nlp_model(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return {"entities": entities}

# 要約エンドポイント
@app.get("/summary", tags=["Summary"])
def summary_endpoint(text: str):
    """入力テキストを要約します。"""
    summary = summarize_text(text)
    return {"summary": summary}

# PubMed 論文検索エンドポイント
@app.get("/search_pubmed", tags=["Search"])
async def search_pubmed(query: str, max_results: int = 10):
    """PubMed で論文を検索します。"""
    pubmed = PubMedClient()
    ids, count = await pubmed.search(query, retmax=max_results)
    return {"query": query, "count": count, "pmid_list": ids}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
@app.get("/paper/{pmid}", tags=["Paper"])
async def get_paper(pmid: str):
    pubmed = PubMedClient()  # api_clients/pubmed_client.py に実装済み
    articles = await pubmed.fetch_details([pmid])
    if not articles:
        raise HTTPException(status_code=404, detail=f"No article found for PMID {pmid}")
    # ここでは最初の記事の情報をそのまま返す例
    return articles[0]
