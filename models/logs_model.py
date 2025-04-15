# models/logs_model.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogEntry(BaseModel):
    id: Optional[int] = None  # 自動採番（実際のDBでは）
    query: str                # 検索キーワード
    result_summary: str       # 要約結果など
    source: str               # "pubmed" / "arxiv" など
    timestamp: datetime       # 実行日時
