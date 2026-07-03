from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/scripts", tags=["web"])
async def page_scripts(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            resp = await c.get(url)
        scripts = re.findall(r"<script[^>]+src=" + Q + r"([^" + Q + r"]+)" + Q, resp.text)
        return {"code": "200", "url": url, "count": len(scripts), "scripts": scripts[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
