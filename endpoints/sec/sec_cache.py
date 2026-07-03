from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx, datetime

@router.get("/sec/cache", tags=["security"])
async def sec_cache(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        h = resp.headers
        return {"code": "200", "url": url,
                "cache_control": h.get("cache-control"),
                "pragma": h.get("pragma"),
                "expires": h.get("expires"),
                "age": h.get("age"),
                "etag": h.get("etag"),
                "last_modified": h.get("last-modified"),
                "no_cache": "no-cache" in h.get("cache-control", "").lower(),
                "no_store": "no-store" in h.get("cache-control", "").lower(),
                "public_cacheable": "public" in h.get("cache-control", "").lower()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
