from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/language", tags=["web"])
async def page_language(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        html_lang = re.search(r"<html[^>]*lang=" + Q + r"([^" + Q + r"]+)" + Q, resp.text[:2000])
        return {"code": "200", "url": url, "html_lang": html_lang.group(1) if html_lang else None,
                "content_type_lang": resp.headers.get("content-language")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
