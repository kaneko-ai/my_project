# Python 3.11の軽量イメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリを/appに設定
WORKDIR /app

# 依存ファイルを先にコピー（requirements.txtなど）
COPY requirements.txt .

# 依存ライブラリをインストール
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ソースコード全体をコピー
COPY . .

# APIサーバーのポート（例: 8000）を公開
EXPOSE 8000

# FastAPIサーバーを起動（ここではuvicornを使用）
CMD ["uvicorn", "ultimate_mygpt:app", "--host", "0.0.0.0", "--port", "8000"]
