import requests
import xml.etree.ElementTree as ET
import json
from typing import List
from models.article_summary import ArticleSummary  # ← モデルを外部から読み込み

# ----- arXivClient の実装 -----
class ArxivClient:
    BASE_URL = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> List[ArticleSummary]:
        url = f"{self.BASE_URL}?search_query=all:{query}&max_results={max_results}"
        response = requests.get(url)
        response.raise_for_status()
        xml_content = response.text

        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        summaries = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else "No Title"
            abstract = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
            authors = [author.find('atom:name', ns).text.strip() for author in entry.findall('atom:author', ns)]
            journal = "arXiv"
            published = entry.find('atom:published', ns).text.strip() if entry.find('atom:published', ns) is not None else ""
            year = int(published[:4]) if published and published[:4].isdigit() else None

            summary_obj = ArticleSummary(
                pmid=None,
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
    BASE_URL = "https://api.biorxiv.org/details/biorxiv/2020-01-01/2023-12-31"

    def search(self, query: str, max_results: int = 10) -> List[ArticleSummary]:
        url = f"{self.BASE_URL}/{query}/{max_results}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        summaries = []
        for item in data.get("collection", []):
            title = item.get("title", "No Title")
            authors = item.get("authors", "").split("; ") if item.get("authors") else []
            journal = "bioRxiv"
            pub_date = item.get("date", "")
            year = int(pub_date[:4]) if pub_date and pub_date[:4].isdigit() else None
            abstract = item.get("abstract", "")
            summary_obj = ArticleSummary(
                pmid=item.get("doi", None),
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                citation=f"{authors[0] if authors else 'Unknown'} et al. ({year}). {title}. {journal}."
            )
            summaries.append(summary_obj)
        return summaries
