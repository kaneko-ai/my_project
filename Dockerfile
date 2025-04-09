FROM python:3.11-slim

WORKDIR /app

# 1) OSレベルで必要なものを入れる（必要に応じて）
RUN apt-get update && apt-get install -y \
    build-essential

# 2) pip, wheel 等をまずアップグレード/インストール
RUN pip install --upgrade pip setuptools wheel

# 3) requirements.txt を使ってライブラリインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) ソースコードをコピー
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000", "-k", "sync"]
