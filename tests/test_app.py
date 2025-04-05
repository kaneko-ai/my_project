# tests/test_app.py

import os
import sys

# ★重要★ 現在のテストファイルのある "tests" フォルダの1階層上（リポジトリのルート）を
# Python の検索パスに追加します。これにより、ultimate_mygpt.py がある場所が認識されます。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# リポジトリのルートにある ultimate_mygpt.py から、FastAPI のインスタンス "app" をインポートします。
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # /health エンドポイントに GET リクエストを送ります
    response = client.get("/health")
    # 返ってくる HTTP ステータスコードが 200（成功）であることを確認します
    assert response.status_code == 200
    data = response.json()
    # レスポンスに "status" キーが含まれているかをチェックします
    assert "status" in data
