from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/methods", tags=["network"])
async def net_methods(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    allowed = []
    for method in ["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"]:
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                resp = await c.request(method, url)
            allowed.append({"method": method, "status": resp.status_code, "allowed": resp.status_code not in (405, 501)})
        except: allowed.append({"method": method, "allowed": False})
    return {"code": "200", "url": url, "methods": allowed}
