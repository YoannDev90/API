from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/sort", tags=["tools"])
async def text_sort(body: TextInput, reverse: bool = Query(default=False), numeric: bool = Query(default=False)):
    lines = body.text.splitlines(keepends=True)
    if numeric: lines.sort(key=lambda x: float(x.strip()), reverse=reverse)
    else: lines.sort(reverse=reverse)
    return {"code": "200", "sorted": "".join(lines), "lines": len(lines)}

