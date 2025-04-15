import logging
import os
from io import StringIO

# ✅ logs フォルダが存在しない場合は作成
os.makedirs("logs", exist_ok=True)

# ロガー設定
logger = logging.getLogger("pubmed_logger")
logger.setLevel(logging.INFO)

# 🔽 ファイル保存（logs/pubmed_rag.log に記録）
file_handler = logging.FileHandler("logs/pubmed_rag.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 🔽 メモリ保存（アプリ内でログを参照するため）
memory_buffer = StringIO()
memory_handler = logging.StreamHandler(memory_buffer)
memory_handler.setLevel(logging.INFO)

# フォーマットを設定（日時＋メッセージ）
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
memory_handler.setFormatter(formatter)

# ロガーにハンドラーを追加
logger.addHandler(file_handler)
logger.addHandler(memory_handler)

# 🔽 ログ保存用の関数（ファイル＋メモリ両方に記録）
def save_log(message: str):
    logger.info(message)

# 🔽 メモリ上のログを取得（画面表示などに使用）
def get_memory_logs():
    memory_buffer.seek(0)
    return memory_buffer.read().splitlines()
