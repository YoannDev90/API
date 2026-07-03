from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

@router.post("/encode/rot47", tags=["encode"])
async def encode_rot47(body: EncodeInput):
    r = []
    for c in body.text:
        o = ord(c)
        if 33 <= o <= 126: r.append(chr(33 + ((o - 33 + 47) % 94)))
        else: r.append(c)
    return {"code": "200", "action": body.action, "result": "".join(r)}
