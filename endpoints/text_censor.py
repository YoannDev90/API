from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import re

@router.post("/text/censor", tags=["text"])
async def text_censor(body: TextInput, words: str = Query(..., description="Comma-separated words to censor"),
                      replacement: str = Query(default="****")):
    t = body.text
    for w in words.split(","):
        w = w.strip()
        if w: t = re.sub(re.escape(w), replacement, t, flags=re.IGNORECASE)
    return {"code": "200", "censored": t}
