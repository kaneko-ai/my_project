# utils/log_storage.py
from models.logs_model import LogEntry
from typing import List
from datetime import datetime

_logs: List[LogEntry] = []  # メモリ内に保存

def save_log(query: str, summary: str, source: str):
    log = LogEntry(
        query=query,
        result_summary=summary,
        source=source,
        timestamp=datetime.now()
    )
    _logs.append(log)

def get_logs() -> List[LogEntry]:
    return _logs[::-1]  # 新しい順に表示
