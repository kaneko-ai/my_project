#!/usr/bin/env python
"""
Extended Paper Clients for MyGPT Paper Analyzer
・PubMed, arXiv, bioRxiv から論文情報の取得機能を提供する
"""

import requests
import xml.etree.ElementTree as ET
import json
from typing import List, Optional
from pydantic import BaseModel, Field

# ----- 既存の ArticleSummary データモデル例 -----
class ArticleSummary(BaseModel):
    pmid: Optional[str] = Field(None, description="論文ID（PubMedの場合）")
    title: str = Field(..., description="論文タイトル")
    authors: List[str] = Field(..., description="著者リスト")
    journal: Optional[str] = Field(None, description="ジャーナル名またはプレプリントサーバー名")
    year: Optional[int] = Field(None, description="発行年")
    abstract: Optional[str] = Field(None, description="要約テキスト")
    citation: Optional[str] = Field(None, description="引用情報")

# ---------------------------------------------------

# ----- arXivClient の実装 -----
class ArxivClient:
    BASE_URL = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> List[ArticleSummary]:
        # URL例: http://export.arxiv.org/api/query?search_query=all:がん&max_results=10
        url = f"{self.BASE_URL}?search_query=all:{query}&max_results={max_results}"
        response = requests.get(url)
        response.raise_for_status()
        xml_content = response.text

        # XML のパース
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}  # 名前空間

        summaries = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else "No Title"
            abstract = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
            # 著者情報の取得（複数あるのでリスト化）
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text.strip() if author.find('atom:name', ns) is not None else "Unknown"
                authors.append(name)
            # arXiv では journal 情報は存在しないが、公開先として "arXiv" と記入
            journal = "arXiv"
            # 発行年は、出版日（publishedタグ）から年だけ抽出
            published = entry.find('atom:published', ns).text.strip() if entry.find('atom:published', ns) is not None else ""
            year = int(published[:4]) if published and published[:4].isdigit() else None

            # 統一フォーマットへ変換
            summary_obj = ArticleSummary(
                pmid=None,  # arXiv の場合特有IDを別途扱う場合あり
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                citation=f"{authors[0] if authors else 'Unknown'} et al. ({year}). {title}. {journal}."
            )
            summaries.append(summary_obj)
        return summaries

# ----- BioRxivClient の実装 -----
class BioRxivClient:
    # bioRxiv API の URL 例 (ここでは2020年〜最新の論文を対象にする例)
    BASE_URL = "https://api.biorxiv.org/details/biorxiv/2020-01-01/2023-12-31"

    def search(self, query: str, max_results: int = 10) -> List[ArticleSummary]:
        # bioRxiv の API はキーワード検索に対応しているので、URL に query パラメータを追加（例としてシンプルに実装）
        url = f"{self.BASE_URL}/{query}/{max_results}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        summaries = []
        # bioRxiv API の返却形式に合わせる（返却の JSON 構造は公式ドキュメントを参照する必要があります）
        for item in data.get("collection", []):
            title = item.get("title", "No Title")
            authors = item.get("authors", "").split("; ") if item.get("authors") else []
            # journal が bioRxiv 固有のものとして設定
            journal = "bioRxiv"
            # 公開日（dateというキーがあると仮定して年を抽出）
            pub_date = item.get("date", "")
            year = int(pub_date[:4]) if pub_date and pub_date[:4].isdigit() else None
            abstract = item.get("abstract", "")
            summary_obj = ArticleSummary(
                pmid=item.get("doi", None),  # DOI を識別子として扱う場合もある
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                citation=f"{authors[0] if authors else 'Unknown'} et al. ({year}). {title}. {journal}."
            )
            summaries.append(summary_obj)
        return summaries

# ----- 使用例：クライアントの呼び出し -----
if __name__ == "__main__":
    query = "がん"
    max_results = 5

    print("----- arXiv の検索結果 -----")
    arxiv_client = ArxivClient()
    arxiv_results = arxiv_client.search(query, max_results)
    for result in arxiv_results:
        print(result.json(indent=2, ensure_ascii=False))

    print("\n----- bioRxiv の検索結果 -----")
    biorxiv_client = BioRxivClient()
    biorxiv_results = biorxiv_client.search(query, max_results)
    for result in biorxiv_results:
        print(result.json(indent=2, ensure_ascii=False))
