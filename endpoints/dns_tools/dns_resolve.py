from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/resolve", tags=["dns"])
async def dns_resolve(domain: str = Query(..., description="Domain name"),
                      resolver_ip: str = Query(default="1.1.1.1", description="Resolver IP"),
                      type: str = Query(default="A", description="Record type")):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [resolver_ip]
        answers = resolver.resolve(domain, type)
        return {"code": "200", "domain": domain, "resolver": resolver_ip, "type": type, "answers": [str(r) for r in answers]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
