# routers/summary.py
from fastapi import APIRouter
from pydantic import BaseModel
from api_clients.pubmed_client import fetch_pubmed_articles
from nlp.summary_model import summarize_text

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/summarize_pubmed")
def summarize_pubmed_query(request: QueryRequest):
    # PubMedから最初の論文の抄録を取得
    abstracts = search_pubmed_and_fetch_abstracts(request.query, max_results=1)
    if not abstracts:
        return {"error": "該当論文が見つかりませんでした"}

    # 要約
    summary = summarize_text(abstracts[0])
    return {
        "original": abstracts[0],
        "summary": summary
    }
