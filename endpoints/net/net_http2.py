from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/http2", tags=["network"])
async def net_http2(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        via = resp.headers.get("via", "").lower()
        upgrade = resp.headers.get("upgrade", "").lower()
        alt_svc = resp.headers.get("alt-svc", "").lower()
        h2 = "h2" in via or "h2" in upgrade or "h2" in alt_svc or resp.http_version in ("HTTP/2", "h2")
        return {"code": "200", "url": url, "http2": h2, "http_version": resp.http_version, "alt_svc": resp.headers.get("alt-svc")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
