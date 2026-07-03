from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx

@router.get("/cookies", tags=["tools"])
async def fetch_cookies(url: str = Query(..., description="URL to fetch")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        cookies = [{"name": k, "value": v} for k, v in c.cookies.items()] if hasattr(c, "cookies") else []
        return {"code": "200", "url": url, "status": resp.status_code, "cookies": cookies}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

