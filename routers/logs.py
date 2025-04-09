from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

@router.get("/recent_logs")
def recent_logs(lines: int = 10):
    log_file = "logs/pubmed_rag.log"
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Log file not found")
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.readlines()
    return {"recent_logs": content[-lines:]}

@router.get("/search_logs")
def search_logs(keyword: str):
    log_file = "logs/pubmed_rag.log"
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Log file not found")
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    matched_lines = [line for line in lines if keyword.lower() in line.lower()]
    return {"matched_logs": matched_lines}
