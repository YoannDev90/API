from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/all", tags=["dns"])
async def dns_all(domain: str = Query(..., description="Domain name")):
    types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    results = {}
    for t in types:
        try:
            answers = dns.resolver.resolve(domain, t)
            results[t] = [str(r) for r in answers]
        except Exception:
            results[t] = []
    return {"code": "200", "domain": domain, "records": results}
