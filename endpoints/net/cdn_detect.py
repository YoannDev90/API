from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

CDNS = {
    "cloudflare": ["cloudflare", "__cfduid"],
    "cloudfront": ["cloudfront", "x-amz-cf"],
    "akamai": ["akamai", "akamaized"],
    "fastly": ["fastly", "x-fastly"],
    "cloudflare": ["cloudflare"],
    "incapsula": ["incapsula", "x-iinfo"],
    "sucuri": ["sucuri", "x-sucuri"],
    "stackpath": ["stackpath"],
    "keycdn": ["keycdn"],
    "cdn77": ["cdn77"],
}

@router.get("/cdn-detect", tags=["network"])
async def cdn_detect(url: str = Query(..., description="Website URL")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        headers_str = str(dict(resp.headers)).lower()
        detected = []
        for name, hints in CDNS.items():
            for h in hints:
                if h.lower() in headers_str:
                    detected.append(name)
                    break
        return {"code": "200", "url": url, "cdn": list(set(detected)) or ["unknown"],
                "server": resp.headers.get("server", "unknown"),
                "via": resp.headers.get("via", "")}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
