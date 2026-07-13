from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import asyncio
from endpoints.web._fetcher import fetch_page

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/schema", tags=["web"])
async def page_schema(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        page_html = await fetch_page(url)
        schemas = []
        for m in re.finditer(r"<script\s+type=" + Q + r"application/ld\+json" + Q + r"[^>]*>(.*?)</script>", page_html, re.DOTALL | re.IGNORECASE):
            try: schemas.append(json.loads(m.group(1)))
            except: pass
        return {"code": "200", "url": url, "count": len(schemas), "schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
