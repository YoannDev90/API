from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/string/repeat", tags=["tools"])
async def string_repeat(body: TextInput, times: int = Query(default=2, ge=1, le=1000)):
    return {"code": "200", "original": body.text, "repeated": body.text * times, "times": times}

