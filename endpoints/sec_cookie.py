from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx, re

@router.get("/sec/cookie", tags=["security"])
async def sec_cookie(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        set_cookie = resp.headers.get_list("set-cookie") if hasattr(resp.headers, "get_list") else [resp.headers.get("set-cookie")] if resp.headers.get("set-cookie") else []
        cookies = []
        for sc in set_cookie:
            parts = sc.split(";")
            name = parts[0].split("=")[0] if "=" in parts[0] else parts[0]
            c_info = {"name": name, "secure": "secure" in sc.lower(), "httponly": "httponly" in sc.lower(),
                      "samesite": "samesite=lax" in sc.lower() or "samesite=strict" in sc.lower(),
                      "path": re.search(r"(?i)path=([^;]+)", sc).group(1) if re.search(r"(?i)path=([^;]+)", sc) else None}
            cookies.append(c_info)
        return {"code": "200", "url": url, "cookies": cookies, "count": len(cookies)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
