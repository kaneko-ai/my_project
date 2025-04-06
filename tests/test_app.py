import os
import sys

# 1. リポジトリのルート（tests の親ディレクトリ）を Python のモジュール検索パスに追加する
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. リポジトリのルートにある ultimate_mygpt.py から FastAPI の app をインポート
from ultimate_mygpt import app

# 3. fastapi.testclient を使ってテストクライアントを作成
from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    """
    /health エンドポイントにアクセスして、ステータスコード200が返るかどうかを確認するテスト。
    """
    response = client.get("/health")
    # ステータスコードが200であることを確認
    assert response.status_code == 200, "Expected status code 200, but got {}".format(response.status_code)
    # レスポンスのJSONを確認
    data = response.json()
    # "status" キーが含まれていることを確認
    assert "status" in data, "'status' key should be in the response JSON"
