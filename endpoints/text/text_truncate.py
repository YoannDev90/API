from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/truncate", tags=["text"])
async def text_truncate(body: TextInput, length: int = Query(default=100, ge=1, le=10000),
                        ellipsis: str = Query(default="..."), word_boundary: bool = Query(default=True)):
    t = body.text
    if len(t) <= length: return {"code": "200", "truncated": t, "truncated": False}
    if word_boundary:
        truncated = t[:length].rsplit(" ", 1)[0] + ellipsis
    else:
        truncated = t[:length] + ellipsis
    return {"code": "200", "original_length": len(t), "truncated": truncated}
