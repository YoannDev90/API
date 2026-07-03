from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

import base64

@router.post("/encode/ascii85", tags=["encode"])
async def encode_ascii85(body: EncodeInput):
    try:
        if body.action == "encode": result = base64.a85encode(body.text.encode()).decode()
        else: result = base64.a85decode(body.text.encode()).decode()
        return {"code": "200", "action": body.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
