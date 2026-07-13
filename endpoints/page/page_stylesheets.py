from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/stylesheets", tags=["web"])
async def page_stylesheets(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        css = re.findall(r"<link[^>]+rel=" + Q + r"stylesheet" + Q + r"[^>]*href=" + Q + r"([^" + Q + r"]+)" + Q, page_html)
        return {"code": "200", "url": url, "count": len(css), "stylesheets": css[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
