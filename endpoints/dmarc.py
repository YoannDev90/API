from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dmarc", tags=["dns"])
async def dmarc_lookup(domain: str = Query(..., description="Domain name")):
    try:
        records = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        dmarc = [str(r) for r in records if str(r).startswith("v=DMARC1")]
        parsed = None
        if dmarc:
            parts = dmarc[0].split(";")
            parsed = {}
            for p in parts:
                p = p.strip()
                if "=" in p:
                    k, v = p.split("=", 1)
                    parsed[k.strip()] = v.strip()
        return {"code": "200", "domain": domain, "has_dmarc": bool(dmarc), "dmarc": parsed, "policy": parsed.get("p", "none") if parsed else "none"}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"code": "200", "domain": domain, "has_dmarc": False, "dmarc": None, "policy": "none"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
