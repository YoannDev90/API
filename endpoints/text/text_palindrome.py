from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import re

@router.post("/text/palindrome", tags=["text"])
async def text_palindrome(body: TextInput):
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", body.text).lower()
    is_pal = cleaned == cleaned[::-1]
    return {"code": "200", "is_palindrome": is_pal, "reversed": body.text[::-1]}
