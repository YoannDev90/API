from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/feeds", tags=["web"])
async def page_feeds(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        feeds = []
        for m in re.finditer(r"<link\s+[^>]*type=" + Q + r"application/(?:rss|atom)\+xml" + Q + r"[^>]*>", page_html, re.IGNORECASE):
            href = re.search(r"href=" + Q + r"([^" + Q + r"]+)" + Q, m.group(0))
            title = re.search(r"title=" + Q + r"([^" + Q + r"]+)" + Q, m.group(0))
            tm = re.search(r"type=" + Q + r"([^" + Q + r"]+)" + Q, m.group(0))
            if href: feeds.append({"href": href.group(1), "title": title.group(1) if title else "", "type": tm.group(1) if tm else ""})
        return {"code": "200", "url": url, "feeds": feeds}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
