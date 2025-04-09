from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SummaryRequest(BaseModel):
    text: str

@router.post("/summary")
async def summarize_text(req: SummaryRequest):
    summary = req.text[:100] + "..." if len(req.text) > 100 else req.text
    return {"summary": summary}
