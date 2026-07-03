from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx

@router.get("/robots", tags=["tools"])
async def fetch_robots(url: str = Query(..., description="Site URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(url.rstrip("/") + "/robots.txt")
        if resp.status_code != 200:
            return {"code": "200", "url": url, "status": resp.status_code, "content": None}
        text = resp.text
        return {"code": "200", "url": url, "disallow": [l.split(":",1)[1].strip() for l in text.splitlines() if l.lower().startswith("disallow")],
                "allow": [l.split(":",1)[1].strip() for l in text.splitlines() if l.lower().startswith("allow")],
                "sitemaps": [l.split(":",1)[1].strip() for l in text.splitlines() if l.lower().startswith("sitemap")], "raw": text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

