from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/links", tags=["web"])
async def page_links(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            resp = await c.get(url)
        links = re.findall(r"href=" + Q + r"([^" + Q + r"]+)" + Q, resp.text)
        links = [l for l in links if not l.startswith(("javascript:", "mailto:", "tel:"))]
        return {"code": "200", "url": url, "count": len(links), "links": links[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
