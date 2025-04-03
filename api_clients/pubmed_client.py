# api_clients/pubmed_client.py
import os, json
from typing import List, Tuple
import httpx

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def search(self, query: str, retmax: int = 10) -> Tuple[List[str], int]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax
        }
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{self.BASE_URL}/esearch.fcgi"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        result = data.get("esearchresult", {})
        count = int(result.get("count", 0))
        id_list = result.get("idlist", [])
        return id_list, count

    # 詳細取得関数は省略（必要に応じて追加）
