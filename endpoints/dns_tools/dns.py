from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import dns.resolver

@router.get("/dns", tags=["utils"])
async def dns_lookup(
    domain: str = Query(..., description="Domain to query"),
    type: str = Query(default="A", description="Record type (A, AAAA, MX, NS, TXT, CNAME, SOA)"),
):
    types_upper = type.upper()
    valid = {"A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR", "SRV", "CAA"}
    if types_upper not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid type. Valid: {', '.join(sorted(valid))}")
    try:
        answers = dns.resolver.resolve(domain, types_upper)
        records = [str(r) for r in answers]
        return {"code": "200", "domain": domain, "type": types_upper, "records": records}
    except dns.resolver.NoAnswer:
        return {"code": "200", "domain": domain, "type": types_upper, "records": []}
    except dns.resolver.NXDOMAIN:
        raise HTTPException(status_code=404, detail="Domain not found")
    except Exception as e:
        logger.error(f"DNS lookup failed for {domain} {type}: {e}")
        raise HTTPException(status_code=502, detail=f"DNS lookup failed: {e}")

