import pytest
from fastapi.testclient import TestClient
from main import app  # main.py の app をインポート

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ようこそ！MyGPTアナライザーへ"
