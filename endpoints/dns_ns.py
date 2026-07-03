from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/ns", tags=["dns"])
async def dns_ns(domain: str = Query(..., description="Domain name")):
    try:
        ns = dns.resolver.resolve(domain, "NS")
        return {"code": "200", "domain": domain, "nameservers": [str(r) for r in ns]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
