from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/http3", tags=["network"])
async def net_http3(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        alt_svc = resp.headers.get("alt-svc", "")
        h3 = "h3" in alt_svc.lower()
        return {"code": "200", "url": url, "http3": h3, "alt_svc": alt_svc}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
