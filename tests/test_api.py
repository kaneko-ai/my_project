import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_register_and_search():
    # 登録データ（シンプル）
    paper_data = {
        "title": "Test Paper on GPT",
        "abstract": "This paper discusses GPT model usage...",
        "metadata": {
            "year": "2024",
            "citations": 42,
            "journal_score": 0.7
        }
    }

    # 1. 登録
    response = client.post("/register", json=paper_data)
    assert response.status_code == 200
    assert "score" in response.json()

    # 2. 検索
    search_query = {"query_text": "GPT model usage"}
    search_response = client.post("/search", json=search_query)
    assert search_response.status_code == 200
    assert isinstance(search_response.json(), list)

def test_get_all_and_top_papers():
    # 3. 全取得
    response_all = client.get("/papers")
    assert response_all.status_code == 200
    assert isinstance(response_all.json(), list)

    # 4. スコア上位取得
    response_top = client.get("/papers/top?limit=5")
    assert response_top.status_code == 200
    data = response_top.json()
    assert isinstance(data, list)
    if data:
        assert "score" in data[0]
