# tests/test_api.py
from fastapi.testclient import TestClient
from ultimate_mygpt import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"

def test_search():
    response = client.get("/search", params={"query": "cancer", "max_results": 5})
    assert response.status_code == 200
    data = response.json()
    # 簡単なチェック：queryキーとresultsキーがあること
    assert "query" in data and "results" in data

def test_paper():
    # 存在しないPMIDの場合のエラーチェック
    response = client.get("/paper/00000000")
    assert response.status_code == 404
