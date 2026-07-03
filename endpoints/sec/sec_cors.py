from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/sec/cors", tags=["security"])
async def sec_cors(url: str = Query(..., description="URL to test")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.options(url, headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "GET"})
        h = resp.headers
        return {"code": "200", "url": url,
                "allow_origin": h.get("access-control-allow-origin"),
                "allow_methods": h.get("access-control-allow-methods"),
                "allow_headers": h.get("access-control-allow-headers"),
                "allow_credentials": h.get("access-control-allow-credentials"),
                "expose_headers": h.get("access-control-expose-headers"),
                "max_age": h.get("access-control-max-age"),
                "wildcard_origin": h.get("access-control-allow-origin") == "*"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
