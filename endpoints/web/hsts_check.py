from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/hsts", tags=["web"])
async def hsts_check(domain: str = Query(..., description="Domain name")):
    url = f"https://{domain}"
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        hsts = resp.headers.get("strict-transport-security", "")
        parsed = {}
        if hsts:
            for part in hsts.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    parsed[k.strip()] = v.strip()
                else:
                    parsed[part] = True
        return {"code": "200", "domain": domain, "hsts": bool(hsts),
                "header": hsts or None, "parsed": parsed or None}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
