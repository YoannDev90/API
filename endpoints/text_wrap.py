from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import textwrap

@router.post("/text/wrap", tags=["text"])
async def text_wrap(body: TextInput, width: int = Query(default=80, ge=10, le=500)):
    wrapped = textwrap.fill(body.text, width=width)
    return {"code": "200", "original": body.text, "wrapped": wrapped, "width": width}
