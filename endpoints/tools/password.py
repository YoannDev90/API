from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import secrets, string

@router.get("/password", tags=["utils"])
async def password(length: int = Query(default=20, ge=4, le=128)):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pw = "".join(secrets.choice(chars) for _ in range(length))
    return {"code": "200", "length": length, "password": pw}

