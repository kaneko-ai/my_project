# tests/test_app.py
import os
import sys

# リポジトリのルートディレクトリ（ultimate_mygpt.pyがある場所）をPythonの検索パスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ultimate_mygpt.py から FastAPI のインスタンス 'app' をインポート
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # /health エンドポイントにGETリクエストを送り、200 OKが返るか確認するテスト
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
