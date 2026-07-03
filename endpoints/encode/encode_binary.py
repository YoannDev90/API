from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

@router.post("/encode/binary", tags=["encode"])
async def encode_binary(body: EncodeInput):
    try:
        if body.action == "encode": result = " ".join(format(ord(c), "08b") for c in body.text)
        else: result = "".join(chr(int(b, 2)) for b in body.text.split())
        return {"code": "200", "action": body.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
