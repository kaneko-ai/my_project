# tests/test_app.py

import os
import sys

# ここで、testsフォルダの1つ上の階層（リポジトリのルート）をPythonの検索パスに追加します。
# こうすることで、ultimate_mygpt.py が存在する場所をPythonに知らせることができます。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# これで、ultimate_mygpt.py から app をインポートできるようになります。
from ultimate_mygpt import app

from fastapi.testclient import TestClient

# TestClient を使って API をテストする準備
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
