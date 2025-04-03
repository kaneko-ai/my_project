# tests/test_app.py
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ner_endpoint():
    response = client.get("/ner", params={"text": "Apple is buying U.K. startup for $1 billion"})
    assert response.status_code == 200
    data = response.json()
    # 固有表現が含まれているか確認する例
    assert any("Apple" in ent for ent in [item[0] for item in data.get("entities", [])])

def test_summary_endpoint():
    text = "Apple is looking at buying U.K. startup for $1 billion. This is a very interesting opportunity."
    response = client.get("/summary", params={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) > 0
