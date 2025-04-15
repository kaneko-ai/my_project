from fastapi import APIRouter, Query
from typing import List
from api_clients.arxiv_biorxiv_client import ArxivClient, BioRxivClient, ArticleSummary

router = APIRouter()

@router.get("/arxiv/search", response_model=List[ArticleSummary])
def search_arxiv(query: str = Query(...), max_results: int = 5):
    client = ArxivClient()
    return client.search(query, max_results)

@router.get("/biorxiv/search", response_model=List[ArticleSummary])
def search_biorxiv(query: str = Query(...), max_results: int = 5):
    client = BioRxivClient()
    return client.search(query, max_results)
