from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver, asyncio

RESOLVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9", "208.67.222.222", "8.26.56.26"]

@router.get("/dns/propagation", tags=["dns"])
async def dns_propagation(domain: str = Query(..., description="Domain name"),
                          type: str = Query(default="A", description="Record type")):
    results = []
    for resolver_ip in RESOLVERS:
        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = [resolver_ip]
            answers = resolver.resolve(domain, type)
            results.append({"resolver": resolver_ip, "status": "ok", "answers": [str(r) for r in answers]})
        except Exception as e:
            results.append({"resolver": resolver_ip, "status": "error", "error": str(e)[:100]})
    return {"code": "200", "domain": domain, "type": type, "results": results}
