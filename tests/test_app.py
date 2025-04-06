# tests/test_app.py

import os
import sys

# ★重要★
# 現在、このテストファイルは tests フォルダにあります。
# そのため、リポジトリのルート（ultimate_mygpt.py がある場所）を Python のモジュール検索パスに追加します。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# リポジトリのルートにある ultimate_mygpt.py から FastAPI のインスタンス app をインポート
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # /health エンドポイントに GET リクエストを送信して、正しいレスポンスが返るか確認するテストです。
    response = client.get("/health")
    # HTTPステータスコードが200（成功）であることを確認
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()
    # レスポンスのJSONに "status" キーが含まれていることを確認
    assert "status" in data, "Response JSON should contain 'status'"
