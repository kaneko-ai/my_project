from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/search")
async def search_pubmed(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="クエリが空です")
    return {"source": "PubMed", "query": query, "results": [{"pmid": "12345", "title": "論文タイトル"}]}
