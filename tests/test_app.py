# tests/test_app.py

import os
import sys

# ★ここが重要★
# このコードは、現在のテストファイル（testsフォルダ内）の「1つ上の階層」、すなわちリポジトリのルートを
# Pythonのモジュール検索パス（sys.path）に追加します。
# これにより、ルートにある ultimate_mygpt.py をインポートできるようになります。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ultimate_mygpt.py から FastAPI のインスタンス app をインポートします。
from ultimate_mygpt import app

# FastAPI の TestClient を使って、API のテストを行います。
from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # "/health" エンドポイントに GET リクエストを送ります。
    response = client.get("/health")
    # 返ってくる HTTP ステータスコードが 200（成功）であることを確認します。
    assert response.status_code == 200
    data = response.json()
    # レスポンスに "status" というキーが含まれているかをチェックします。
    assert "status" in data
