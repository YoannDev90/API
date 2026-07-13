from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/links", tags=["web"])
async def page_links(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        links = re.findall(r"href=" + Q + r"([^" + Q + r"]+)" + Q, page_html)
        links = [l for l in links if not l.startswith(("javascript:", "mailto:", "tel:"))]
        return {"code": "200", "url": url, "count": len(links), "links": links[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
