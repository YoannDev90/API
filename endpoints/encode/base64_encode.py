from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import base64

class B64Input(BaseModel):
    data: str = Field(..., description="String to encode/decode")

@router.post("/base64/encode", tags=["utils"])
async def base64_encode(body: B64Input):
    encoded = base64.urlsafe_b64encode(body.data.encode()).rstrip(b"=").decode()
    return {"code": "200", "encoded": encoded}

