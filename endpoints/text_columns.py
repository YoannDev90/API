from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/columns", tags=["tools"])
async def text_columns(body: TextInput, col: int = Query(default=1, ge=1, description="Column number (1-indexed)"),
                       delimiter: str = Query(default=" ", description="Column delimiter")):
    extracted = []
    for line in body.text.splitlines():
        parts = line.split(delimiter)
        if col <= len(parts): extracted.append(parts[col-1])
    return {"code": "200", "column": col, "delimiter": delimiter, "values": extracted, "count": len(extracted)}

