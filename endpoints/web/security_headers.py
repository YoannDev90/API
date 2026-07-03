from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/headers/security", tags=["web"])
async def security_headers(url: str = Query(..., description="URL to check")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    GOOD = {"strict-transport-security", "x-content-type-options", "x-frame-options",
             "content-security-policy", "x-xss-protection", "referrer-policy",
             "permissions-policy", "cross-origin-opener-policy", "cross-origin-embedder-policy"}
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        present = {k: resp.headers[k] for k in resp.headers if k.lower() in GOOD}
        missing = sorted(GOOD - {k.lower() for k in resp.headers})
        score = round((len(present) / len(GOOD)) * 100, 1)
        return {"code": "200", "url": url, "score": score, "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F",
                "present": present, "missing": missing}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
