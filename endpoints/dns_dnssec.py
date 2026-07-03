from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver, dns.dnssec

@router.get("/dns/dnssec", tags=["dns"])
async def dns_dnssec(domain: str = Query(..., description="Domain name")):
    try:
        answers = dns.resolver.resolve(domain, "DNSKEY")
        validated = False
        try:
            dns.dnssec.validate(answers, answers)
            validated = True
        except Exception:
            pass
        return {"code": "200", "domain": domain, "has_dnssec": True, "validated": validated, "keys": len(answers)}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"code": "200", "domain": domain, "has_dnssec": False}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
