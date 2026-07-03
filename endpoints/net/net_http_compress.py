from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/http-compress", tags=["network"])
async def net_http_compress(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    supported = []
    for enc in ["gzip", "deflate", "br", "zstd"]:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(url, headers={"Accept-Encoding": enc})
            if resp.headers.get("content-encoding") == enc: supported.append(enc)
        except: pass
    return {"code": "200", "url": url, "supported_compression": supported}
