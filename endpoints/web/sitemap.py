from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx, re

@router.get("/sitemap", tags=["tools"])
async def fetch_sitemap(url: str = Query(..., description="Sitemap URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.get(url)
        if resp.status_code != 200: return {"code": "200", "url": url, "status": resp.status_code, "urls": None}
        urls = re.findall(r"<loc>(.*?)</loc>", resp.text)
        return {"code": "200", "url": url, "count": len(urls), "urls": urls[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

