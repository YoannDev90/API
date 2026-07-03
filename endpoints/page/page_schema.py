from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/page/schema", tags=["web"])
async def page_schema(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            resp = await c.get(url)
        schemas = []
        for m in re.finditer(r"<script\s+type=" + Q + r"application/ld\+json" + Q + r"[^>]*>(.*?)</script>", resp.text, re.DOTALL | re.IGNORECASE):
            try: schemas.append(json.loads(m.group(1)))
            except: pass
        return {"code": "200", "url": url, "count": len(schemas), "schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
