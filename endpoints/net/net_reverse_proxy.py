from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/reverse-proxy", tags=["network"])
async def net_reverse_proxy(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        h = {k.lower(): v for k, v in resp.headers.items()}
        headers_str = str(resp.headers).lower()
        proxies = []
        if "cloudflare" in headers_str or "__cfduid" in str(dict(resp.headers)): proxies.append("Cloudflare")
        if "x-amz-cf" in headers_str: proxies.append("CloudFront")
        if "akamai" in headers_str or "x-akamai" in headers_str: proxies.append("Akamai")
        if "fastly" in headers_str: proxies.append("Fastly")
        if "x-sucuri" in headers_str: proxies.append("Sucuri")
        if "x-iinfo" in headers_str: proxies.append("Incapsula")
        if "via" in h or "x-via" in h or "x-cache" in h: proxies.append("CDN (via/cache headers)")
        return {"code": "200", "url": url, "reverse_proxy": proxies or ["none detected"],
                "server": h.get("server"), "via": h.get("via"), "x-powered-by": h.get("x-powered-by")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
