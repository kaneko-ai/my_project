# -*- coding: utf-8 -*-
"""
OpenAlex API クライアント

DOI や PMID から引用数・著者・概念などの補完情報を取得する
"""

import requests

OPENALEX_BASE_URL = "https://api.openalex.org/works/"

def fetch_openalex_data_by_doi(doi: str) -> dict:
    """DOIからOpenAlexの論文情報を取得する"""
    if not doi:
        return {}

    # フォーマット変換（"10.xxxx/..." -> "https://doi.org/10.xxxx/..."）
    doi_url = f"https://doi.org/{doi.lower().strip()}"
    openalex_url = f"{OPENALEX_BASE_URL}doi:{doi_url}"

    try:
        res = requests.get(openalex_url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[OpenAlex] DOI取得失敗: {doi} ({e})")
        return {}

def extract_metadata_from_openalex(oa_data: dict) -> dict:
    """OpenAlexデータから必要な評価情報だけ抽出する"""
    if not oa_data:
        return {}

    return {
        "citation_count": oa_data.get("cited_by_count", 0),
        "concepts": [c["display_name"] for c in oa_data.get("concepts", [])],
        "authorships": oa_data.get("authorships", []),
        # Altmetric-like metricも将来的に使える:
        "altmetric_data": {
            "score": oa_data.get("counts_by_year", [{}])[0].get("cited_by_count", 0)
        }
    }
