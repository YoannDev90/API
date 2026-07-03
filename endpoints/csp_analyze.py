from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx, re

@router.get("/csp-analyze", tags=["web"])
async def csp_analyze(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        csp = resp.headers.get("content-security-policy", "")
        if not csp: return {"code": "200", "url": url, "has_csp": False, "directives": None}
        directives = {}
        for d in csp.split(";"):
            d = d.strip()
            if d:
                parts = d.split(None, 1)
                directives[parts[0]] = parts[1] if len(parts) > 1 else ""
        return {"code": "200", "url": url, "has_csp": True, "directives": directives,
                "has_unsafe_inline": "'unsafe-inline'" in csp,
                "has_unsafe_eval": "'unsafe-eval'" in csp,
                "has_wildcard": "*" in csp}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
