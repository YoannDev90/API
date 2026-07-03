from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import re
import httpx

logger = getLogger("api-proxy")
router = APIRouter()

@router.get("/sec/sri", tags=["security"])
async def sec_sri(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        scripts = re.findall(r"<script[^>]+src=" + Q + r"([^" + Q + r"]+)" + Q + r"[^>]*>", resp.text, re.IGNORECASE)
        with_sri = sum(1 for s in scripts if "integrity=" in resp.text[resp.text.find(s)-100:resp.text.find(s)+100] if s in resp.text)
        return {"code": "200", "url": url, "external": len(scripts), "with_sri": with_sri}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
