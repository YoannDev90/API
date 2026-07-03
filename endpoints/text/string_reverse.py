from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/string/reverse", tags=["tools"])
async def string_reverse(body: TextInput):
    return {"code": "200", "original": body.text, "reversed": body.text[::-1]}

