from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/opengraph", tags=["web"])
async def page_opengraph(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        tags = {}
        for m in re.finditer(r"<meta\s+(?:property|name)=" + Q + r"(og:[^" + Q + r"]+)" + Q + r"\s+content=" + Q + r"([^" + Q + r"]+)" + Q, page_html, re.IGNORECASE):
            tags[m.group(1)] = m.group(2)
        return {"code": "200", "url": url, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
