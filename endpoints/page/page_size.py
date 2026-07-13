from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx, time

@router.get("/page/size", tags=["web"])
async def page_size(url: str = Query(..., description="Page URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        start = time.time()
        page_html = await fetch_page(url)
        elapsed = round((time.time() - start) * 1000, 1)
        return {"code": "200", "url": url, "size_bytes": len(resp.content), "size_kb": round(len(resp.content)/1024, 2),
                "load_time_ms": elapsed, "status": resp.status_code, "content_type": {}.get("content-type", "")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
