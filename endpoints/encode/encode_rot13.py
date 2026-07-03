from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

import codecs

@router.post("/encode/rot13", tags=["encode"])
async def encode_rot13(body: EncodeInput):
    return {"code": "200", "action": body.action, "result": codecs.encode(body.text, "rot_13")}
