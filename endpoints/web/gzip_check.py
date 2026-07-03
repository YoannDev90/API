from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/gzip", tags=["web"])
async def gzip_check(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(url, headers={"Accept-Encoding": "gzip, deflate, br"})
        enc = resp.headers.get("content-encoding", "none")
        return {"code": "200", "url": url, "compressed": enc != "none",
                "encoding": enc, "content_type": resp.headers.get("content-type", "")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
