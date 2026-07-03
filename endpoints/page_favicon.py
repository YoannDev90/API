from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/favicon", tags=["web"])
async def page_favicon(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        favicons = []
        for m in re.finditer(r"<link\s+[^>]*rel=" + Q + r".*?icon.*?" + Q + r"[^>]*>", resp.text, re.IGNORECASE):
            href = re.search(r"href=" + Q + r"([^" + Q + r"]+)" + Q, m.group(0))
            sizes = re.search(r"sizes=" + Q + r"([^" + Q + r"]+)" + Q, m.group(0))
            if href: favicons.append({"href": href.group(1), "sizes": sizes.group(1) if sizes else "", "type": "icon"})
        if not favicons:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            favicons.append({"href": f"{parsed.scheme}://{parsed.netloc}/favicon.ico", "sizes": "", "type": "default"})
        return {"code": "200", "url": url, "favicons": favicons}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
