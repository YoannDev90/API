from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/net/ipv6", tags=["network"])
async def net_ipv6(domain: str = Query(..., description="Domain name")):
    a = aaaa = False
    try: a = bool(dns.resolver.resolve(domain, "A"))
    except: pass
    try: aaaa = bool(dns.resolver.resolve(domain, "AAAA"))
    except: pass
    return {"code": "200", "domain": domain, "has_ipv4": a, "has_ipv6": aaaa, "dual_stack": a and aaaa}
