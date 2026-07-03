from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import urllib.parse

@router.get("/url/compare", tags=["web"])
async def url_compare(a: str = Query(..., description="First URL"),
                      b: str = Query(..., description="Second URL")):
    def norm(u):
        if not u.startswith(("http://", "https://")): u = "https://" + u
        p = urllib.parse.urlparse(u)
        return urllib.parse.ParseResult(
            p.scheme, p.hostname.lower() if p.hostname else "", p.path.rstrip("/") or "/",
            p.params, p.query, ""
        )
    na, nb = norm(a), norm(b)
    return {"code": "200", "url_a": a, "url_b": b, "equal": na == nb,
            "normalized_a": urllib.parse.urlunparse(na),
            "normalized_b": urllib.parse.urlunparse(nb)}
