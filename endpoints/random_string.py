from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import secrets, string

@router.get("/random/string", tags=["tools"])
async def random_string(length: int = Query(default=12, ge=1, le=256),
                        digits: bool = Query(default=True), lowercase: bool = Query(default=True),
                        uppercase: bool = Query(default=True), special: bool = Query(default=False)):
    chars = ""
    if digits: chars += string.digits
    if lowercase: chars += string.ascii_lowercase
    if uppercase: chars += string.ascii_uppercase
    if special: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not chars: chars = string.ascii_letters
    return {"code": "200", "length": length, "random_string": "".join(secrets.choice(chars) for _ in range(length))}

