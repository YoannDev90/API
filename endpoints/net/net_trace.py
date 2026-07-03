from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/trace", tags=["network"])
async def net_trace(url: str = Query(..., description="URL to trace")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as c:
            hops = []
            for _ in range(20):
                resp = await c.request("TRACE", url)
                hops.append({"url": url, "status": resp.status_code, "headers": dict(resp.headers)})
                if resp.status_code in (301, 302, 303, 307, 308):
                    url = resp.headers.get("location", "")
                    if not url: break
                else: break
        return {"code": "200", "hops": hops}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
