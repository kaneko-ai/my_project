import pytest
from fastapi.testclient import TestClient
from ultimate_mygpt import app
import datetime

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Hello, World!" in data.get("message", "")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    # タイムスタンプが正しいフォーマットか簡易チェック
    datetime.datetime.strptime(data.get("timestamp"), "%Y-%m-%d_%H-%M-%S")

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data.get("version") == "2.0.0"
    assert "build_time" in data
    assert "platform" in data

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "running"
    assert "base_dir" in data
