# app/api_clients/pubmed_client.py

from typing import List
from Bio import Entrez
from pydantic import BaseModel

# PubMed API使用時にメールアドレスを指定（Entrez規定）
Entrez.email = "kaneko.yu.r3@dc.tohoku.ac.jp"  # ←後で .env に逃がしてOK

class PubMedArticle(BaseModel):
    title: str
    abstract: str

def fetch_pubmed_articles(query: str, max_results: int = 5) -> List[PubMedArticle]:
    """PubMed APIから論文を検索して要約情報を取得"""
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    ids = record["IdList"]

    articles: List[PubMedArticle] = []

    if not ids:
        return articles

    fetch_handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
    fetch_records = Entrez.read(fetch_handle)

    for article in fetch_records["PubmedArticle"]:
        try:
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = article["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0]
            articles.append(PubMedArticle(title=title, abstract=str(abstract)))
        except KeyError:
            continue  # abstractがない論文はスキップ

    return articles
