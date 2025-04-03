# tests/test_app.py
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ner():
    response = client.get("/ner", params={"text": "Apple is buying U.K. startup for $1 billion"})
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert ["Apple", "ORG"] in data["entities"]
