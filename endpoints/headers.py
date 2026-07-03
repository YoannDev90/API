from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx

@router.get("/headers", tags=["tools"])
async def fetch_headers(url: str = Query(..., description="URL to fetch")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as c:
            resp = await c.get(url)
        return {"code": "200", "url": url, "status": resp.status_code, "headers": dict(resp.headers)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

