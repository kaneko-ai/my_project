# Dockerfile
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存ファイルをコピーし、ライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコード全体をコピー
COPY . .

# Render 環境では $PORT 環境変数が自動設定されます
ENV PORT=8000

# ポート番号を公開（Render では必須ではありませんが推奨）
EXPOSE $PORT

# コンテナ起動時のコマンド
CMD ["uvicorn", "ultimate_mygpt:app", "--host=0.0.0.0", "--port", "$PORT"]
