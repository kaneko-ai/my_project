# tests/test_app.py
import sys
import os

# ここで、テストファイルがある「tests」フォルダの1つ上（つまりリポジトリのルート）をPythonに教えます。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# これで、リポジトリのルートにある ultimate_mygpt.py をインポートできるようになります。
from ultimate_mygpt import app

from fastapi.testclient import TestClient
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # "status"キーが含まれているかを確認
    assert "status" in data
