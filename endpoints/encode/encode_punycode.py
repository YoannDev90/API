from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class EncodeInput(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    action: str = Field(default="encode", description="encode or decode")

@router.post("/encode/punycode", tags=["encode"])
async def encode_punycode(body: EncodeInput):
    try:
        if body.action == "encode": result = body.text.encode("idna").decode()
        else: result = body.text.encode().decode("idna")
        return {"code": "200", "action": body.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
