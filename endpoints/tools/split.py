from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class SplitInput(BaseModel):
    text: str = Field(..., description="Text to split")
    delimiter: str = Field(default=",", description="Delimiter")

@router.post("/split", tags=["tools"])
async def split_text(body: SplitInput):
    parts = body.text.split(body.delimiter)
    return {"code": "200", "delimiter": body.delimiter, "count": len(parts), "parts": parts}

