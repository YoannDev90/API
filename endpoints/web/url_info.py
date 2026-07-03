from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import urllib.parse

@router.get("/url/info", tags=["web"])
async def url_info(url: str = Query(..., description="URL to parse")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(p.query)
    return {"code": "200", "url": url,
            "scheme": p.scheme, "hostname": p.hostname, "port": p.port,
            "path": p.path, "query": p.query, "fragment": p.fragment,
            "params": {k: v[0] if len(v) == 1 else v for k, v in q.items()} if q else None}
