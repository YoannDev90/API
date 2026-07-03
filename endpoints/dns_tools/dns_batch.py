from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/batch", tags=["dns"])
async def dns_batch(domain: str = Query(..., description="Domain name"),
                    types: str = Query(default="A,MX,NS,TXT", description="Comma-separated record types")):
    results = {}
    for t in types.split(","):
        t = t.strip().upper()
        try:
            answers = dns.resolver.resolve(domain, t)
            results[t] = [str(r) for r in answers]
        except Exception:
            results[t] = []
    return {"code": "200", "domain": domain, "records": results}
