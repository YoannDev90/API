from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from collections import Counter
from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/string/count", tags=["tools"])
async def string_count(body: TextInput):
    return {"code": "200", "length": len(body.text), "char_frequency": dict(Counter(body.text).most_common(50))}

