from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import base64

class B64Input(BaseModel):
    data: str = Field(..., description="String to encode/decode")

@router.post("/base64/decode", tags=["utils"])
async def base64_decode(body: B64Input):
    try:
        decoded = base64.urlsafe_b64decode(body.data + "==")
        return {"code": "200", "decoded": decoded.decode()}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64")

