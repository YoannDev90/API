from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver, dns.query, dns.zone, asyncio

@router.get("/dns/zone-transfer", tags=["dns"])
async def dns_zone_transfer(domain: str = Query(..., description="Domain name")):
    try:
        ns_records = dns.resolver.resolve(domain, "NS")
        nameservers = [str(r) for r in ns_records]
    except: return {"code": "200", "domain": domain, "zone_transfer_possible": False, "nameservers": [], "records": None}

    results = []
    for ns in nameservers:
        try:
            z = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=5, lifetime=10))
            records = [(str(name), str(rdtype), str(rdata)) for name, node in z.nodes.items() for rdtype, rdata in node.rdatasets.items() for _ in rdata]
            results.append({"nameserver": ns, "success": True, "records": records[:500]})
        except Exception as e:
            results.append({"nameserver": ns, "success": False, "error": str(e)[:100]})
    zone_transfer = any(r["success"] for r in results)
    return {"code": "200", "domain": domain, "zone_transfer_possible": zone_transfer, "nameservers": nameservers, "results": results}
