from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx

@router.get("/redirects", tags=["tools"])
async def trace_redirects(url: str = Query(..., description="URL to trace")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        chain = []
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as c:
            for _ in range(20):
                resp = await c.get(url)
                chain.append({"url": url, "status": resp.status_code})
                if resp.status_code in (301,302,303,307,308): url = resp.headers.get("location","")
                else: break
        return {"code": "200", "chain": chain, "hops": len(chain)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

