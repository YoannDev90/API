from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class SplitInput(BaseModel):
    text: str = Field(..., description="Text to join")
    delimiter: str = Field(default=",", description="Delimiter")

@router.post("/join", tags=["tools"])
async def join_text(body: SplitInput):
    return {"code": "200", "delimiter": body.delimiter, "result": body.delimiter.join(body.text.splitlines())}

