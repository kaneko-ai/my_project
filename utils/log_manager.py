import logging

logger = logging.getLogger("pubmed_logger")
logger.setLevel(logging.INFO)

# ファイル保存
file_handler = logging.FileHandler("logs/pubmed_rag.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# メモリ保存
from io import StringIO
memory_buffer = StringIO()
memory_handler = logging.StreamHandler(memory_buffer)
memory_handler.setLevel(logging.INFO)

# ロガーフォーマット共通
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
memory_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(memory_handler)

def save_log(message: str):
    logger.info(message)

def get_memory_logs():
    memory_buffer.seek(0)
    return memory_buffer.read().splitlines()
