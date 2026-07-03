from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/net/dns-resolve6", tags=["network"])
async def net_dns_resolve6(domain: str = Query(..., description="Domain name")):
    try:
        a = dns.resolver.resolve(domain, "A")
        aaaa = dns.resolver.resolve(domain, "AAAA")
        return {"code": "200", "domain": domain, "a": [str(r) for r in a], "aaaa": [str(r) for r in aaaa]}
    except dns.resolver.NoAnswer: return {"code": "200", "domain": domain, "a": [], "aaaa": []}
    except Exception as e: raise HTTPException(status_code=502, detail=str(e))
