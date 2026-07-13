from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = getLogger("api-proxy")
router = APIRouter()


class BcryptInput(BaseModel):
    password: str = Field(..., description="Password to hash")
    verify: str = Field(default=None, description="Hash to verify against")


@router.post("/bcrypt", tags=["tools"])
async def bcrypt_hash(body: BcryptInput):
    try:
        import bcrypt as bc
        if body.verify:
            result = bc.checkpw(body.password.encode(), body.verify.encode())
            return {"code": "200", "match": result}
        else:
            hashed = bc.hashpw(body.password.encode(), bc.gensalt())
            return {"code": "200", "hash": hashed.decode()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bcrypt error: {e}")
