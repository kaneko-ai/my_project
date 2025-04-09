from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class EmbedRequest(BaseModel):
    text: Optional[str] = None
    pmid: Optional[str] = None

@router.post("/embed")
async def embed_text(req: EmbedRequest):
    if not req.text and not req.pmid:
        raise HTTPException(status_code=400, detail="text または pmid を指定してください")
    return {"embedding": [0.1] * 384}
