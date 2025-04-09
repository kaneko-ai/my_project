from fastapi import APIRouter, HTTPException, Query
from typing import List
from models.article import ArticleSummary
from utils.summarizer import summarizer
from api_clients.pubmed_client import fetch_pubmed_articles
from utils.log_manager import save_log  # ← 追加！

router = APIRouter()

@router.get("/summary", response_model=List[ArticleSummary])
def summarize_articles(
    query: str = Query(..., description="検索キーワード"),
    max_results: int = 5
):
    articles = fetch_pubmed_articles(query, max_results)
    if not articles:
        raise HTTPException(status_code=404, detail="論文が見つかりませんでした")

    summaries = []
    for article in articles:
        summary_text = summarizer(article.abstract)
        summary = ArticleSummary(
            title=article.title,
            abstract=article.abstract,
            authors=[],
            journal="PubMed",
            year=None,
            citation=None
        )
        summary.abstract = summary_text
        summaries.append(summary)

        # ✅ ログに保存（ファイル＆メモリ）
        save_log(f"[要約] {article.title} → {summary_text}")

    return summaries
