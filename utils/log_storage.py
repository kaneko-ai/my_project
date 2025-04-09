from typing import List
from models.logs_model import LogEntry
from datetime import datetime
import os

# メモリログ
_log_store: List[LogEntry] = []

# 保存先ファイル
LOG_FILE_PATH = "logs/pubmed_rag.log"

def save_log(source: str, message: str) -> None:
    """メモリとファイルの両方にログを保存"""
    log_entry = LogEntry(timestamp=datetime.now(), source=source, message=message)

    # メモリに追加
    _log_store.append(log_entry)

    # ファイルに追記
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{log_entry.timestamp.isoformat()} | {source} | {message}\n")

def get_logs() -> List[LogEntry]:
    """メモリ上のログ一覧を取得"""
    return _log_store
