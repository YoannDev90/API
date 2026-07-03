from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import random

@router.post("/text/shuffle", tags=["text"])
async def text_shuffle(body: TextInput, seed: int = Query(default=None, description="Random seed")):
    if seed is not None: random.seed(seed)
    lines = body.text.splitlines()
    random.shuffle(lines)
    return {"code": "200", "shuffled": "\n".join(lines), "lines": len(lines)}
