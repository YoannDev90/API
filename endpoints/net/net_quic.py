from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/quic", tags=["network"])
async def net_quic(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        alt_svc = resp.headers.get("alt-svc", "")
        h3 = "h3" in alt_svc.lower()
        quic_versions = []
        for part in alt_svc.split(","):
            if "h3" in part:
                quic_versions.append(part.strip())
        return {"code": "200", "url": url, "quic_supported": h3, "alt_svc": alt_svc, "quic_versions": quic_versions}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
