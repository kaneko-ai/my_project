# tests/test_app.py

import os
import sys

# -------------------------------
# ここから大事な部分です！
# 現在、このテストファイルは "tests" フォルダにありますが、
# ルートディレクトリ（my_project/ 直下）にある "ultimate_mygpt.py" を
# インポートするために、"tests" の1つ上の階層を探すように指定します。
# -------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# これにより、リポジトリのルートが Python のモジュール検索パスに追加されます。

# ここで "ultimate_mygpt.py" から FastAPI のインスタンス "app" をインポートします
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    # "/health" エンドポイントに GET リクエストを送信
    response = client.get("/health")
    # 返ってくるステータスコードが 200 (OK) であることを確認
    assert response.status_code == 200
    data = response.json()
    # レスポンスに "status" というキーが含まれているかをチェック
    assert "status" in data
