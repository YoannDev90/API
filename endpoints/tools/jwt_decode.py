from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class JWTInput(BaseModel):
    token: str = Field(..., description="JWT token")

@router.post("/jwt/decode", tags=["utils"])
async def jwt_decode(body: JWTInput):
    try:
        import jwt
        header = jwt.get_unverified_header(body.token)
        payload = jwt.decode(body.token, options={"verify_signature": False})
        return {"code": "200", "header": header, "payload": payload}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JWT decode failed: {e}")

