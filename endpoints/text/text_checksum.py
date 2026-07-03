from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

import zlib, hashlib

@router.post("/text/checksum", tags=["text"])
async def text_checksum(body: TextInput):
    data = body.text.encode()
    return {"code": "200", "crc32": f"{zlib.crc32(data):08x}", "adler32": f"{zlib.adler32(data):08x}",
            "md5": hashlib.md5(data).hexdigest(), "sha1": hashlib.sha1(data).hexdigest()}
