# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from app import app  # app.py に定義された FastAPI インスタンス

client = TestClient(app)

def test_ner_endpoint():
    # テキストに "Apple" が含まれている場合、entitiesに ("Apple", "ORG") が含まれることを期待
    response = client.get("/ner", params={"text": "Apple is buying U.K. startup for $1 billion"})
    assert response.status_code == 200
    data = response.json()
    # data["entities"] が存在し、その中に "Apple" が含まれているか確認
    assert "entities" in data
    # 例として、entitiesがリストであり、最初の要素の0番目に "Apple" が含まれているかチェック
    assert any("Apple" in ent for ent in [item[0] for item in data["entities"]])

def test_summary_endpoint():
    text = "Apple is looking at buying U.K. startup for $1 billion. This is a very interesting opportunity."
    response = client.get("/summary", params={"text": text})
    assert response.status_code == 200
    data = response.json()
    # summary が返されることを確認
    assert "summary" in data
