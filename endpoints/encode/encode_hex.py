from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

import binascii

@router.post("/encode/hex", tags=["encode"])
async def encode_hex(body: EncodeInput):
    try:
        if body.action == "encode": result = body.text.encode().hex()
        else: result = bytes.fromhex(body.text).decode()
        return {"code": "200", "action": body.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
