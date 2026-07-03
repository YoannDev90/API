from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import re

@router.post("/text/strip", tags=["text"])
async def text_strip(body: TextInput, mode: str = Query(default="all", description="all|spaces|html|special")):
    t = body.text
    if mode in ("all", "spaces"): t = re.sub(r"\s+", " ", t).strip()
    if mode in ("all", "html"): t = re.sub(r"<[^>]+>", "", t)
    if mode in ("all", "special"): t = re.sub(r"[^a-zA-Z0-9\s]", "", t)
    return {"code": "200", "original": body.text, "stripped": t, "mode": mode}
