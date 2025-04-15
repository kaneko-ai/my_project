from typing import List, Optional
from pydantic import BaseModel, Field

class ArticleSummary(BaseModel):
    pmid: Optional[str] = Field(None, description="論文ID（PubMedの場合）")
    title: str = Field(..., description="論文タイトル")
    authors: List[str] = Field(..., description="著者リスト")
    journal: Optional[str] = Field(None, description="ジャーナル名またはプレプリントサーバー名")
    year: Optional[int] = Field(None, description="発行年")
    abstract: Optional[str] = Field(None, description="要約テキスト")
    citation: Optional[str] = Field(None, description="引用情報")
