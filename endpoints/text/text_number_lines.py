from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/number-lines", tags=["text"])
async def text_number_lines(body: TextInput, start: int = Query(default=1, ge=0), padding: int = Query(default=0, ge=0, le=10)):
    lines = body.text.splitlines()
    fmt = f"{{:>{padding}d}}" if padding else "{}"
    numbered = [f"{fmt.format(i+start)}  {l}" for i, l in enumerate(lines)]
    return {"code": "200", "numbered": "\n".join(numbered), "lines": len(lines)}
