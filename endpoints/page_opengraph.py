from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/opengraph", tags=["web"])
async def page_opengraph(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            resp = await c.get(url)
        tags = {}
        for m in re.finditer(r"<meta\s+(?:property|name)=" + Q + r"(og:[^" + Q + r"]+)" + Q + r"\s+content=" + Q + r"([^" + Q + r"]+)" + Q, resp.text, re.IGNORECASE):
            tags[m.group(1)] = m.group(2)
        return {"code": "200", "url": url, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
