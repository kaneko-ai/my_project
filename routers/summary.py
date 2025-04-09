# routers/summary.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import os

router = APIRouter()

# HuggingFaceの要約モデルを読み込み
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

class SummaryRequest(BaseModel):
    text: str

@router.post("/summary")
async def summarize_text(request: SummaryRequest):
    try:
        result = summarizer(request.text, max_length=130, min_length=30, do_sample=False)
        return {"summary": result[0]["summary_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
