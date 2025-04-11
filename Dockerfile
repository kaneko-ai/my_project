# ✅ 軽量ベース + キャッシュ効率化 + 起動固定
FROM python:3.10-slim

# 環境変数でUTF-8とバッファリング設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Tokyo \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 作業ディレクトリ
WORKDIR /app

# 必要パッケージだけインストール（余計なaptは排除）
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリコード一式コピー
COPY . .

# ポート7860を明示（Gradio UI用）
EXPOSE 7860

# Gradioアプリ起動（必ず0.0.0.0指定）
CMD ["python", "app/gradio_app.py"]
