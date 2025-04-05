# tests/test_app.py

import os
import sys

# ★非常に重要★
# ここで、テストファイル (tests) の親ディレクトリ、つまりリポジトリのルートを
# Python のモジュール検索パスに追加します。これにより、リポジトリのルートにある ultimate_mygpt.py を見つけられます。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ルートにある ultimate_mygpt.py から FastAPI のインスタンス "app" をインポート
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # /health エンドポイントに GET リクエストを送り、正しい応答が返るか確認するテストです。
    response = client.get("/health")
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()
    assert "status" in data, "Response JSON should contain 'status'"
