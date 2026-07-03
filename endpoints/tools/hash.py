from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import hashlib

class HashInput(BaseModel):
    text: str = Field(..., description="Text to hash")

@router.post("/hash", tags=["utils"])
async def hash_text(body: HashInput):
    text = body.text.encode()
    return {
        "code": "200", "input": body.text,
        "md5": hashlib.md5(text).hexdigest(),
        "sha1": hashlib.sha1(text).hexdigest(),
        "sha256": hashlib.sha256(text).hexdigest(),
        "sha512": hashlib.sha512(text).hexdigest(),
    }

