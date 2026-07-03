from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/dedup", tags=["tools"])
async def text_dedup(body: TextInput):
    seen = set(); result = []
    for line in body.text.splitlines():
        if line not in seen: seen.add(line); result.append(line)
    return {"code": "200", "deduped": "\n".join(result), "original_lines": len(body.text.splitlines()), "unique_lines": len(result)}

