from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/language", tags=["web"])
async def page_language(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        html_lang = re.search(r"<html[^>]*lang=" + Q + r"([^" + Q + r"]+)" + Q, page_html[:2000])
        return {"code": "200", "url": url, "html_lang": html_lang.group(1) if html_lang else None,
                "content_type_lang": {}.get("content-language")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
