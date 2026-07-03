from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

import quopri

@router.post("/encode/quoted-printable", tags=["encode"])
async def encode_qp(body: EncodeInput):
    try:
        if body.action == "encode": result = quopri.encodestring(body.text.encode()).decode()
        else: result = quopri.decodestring(body.text.encode()).decode()
        return {"code": "200", "action": body.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
