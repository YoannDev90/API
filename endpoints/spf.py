from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/spf", tags=["dns"])
async def spf_lookup(domain: str = Query(..., description="Domain name")):
    try:
        records = dns.resolver.resolve(domain, "TXT")
        spf_records = [str(r) for r in records if str(r).startswith("v=spf1")]
        parsed = None
        if spf_records:
            parts = spf_records[0].split()
            parsed = {"raw": spf_records[0], "mechanisms": []}
            for p in parts[1:]:
                parsed["mechanisms"].append(p)
        return {"code": "200", "domain": domain, "has_spf": bool(spf_records), "spf": parsed}
    except dns.resolver.NoAnswer:
        return {"code": "200", "domain": domain, "has_spf": False, "spf": None}
    except dns.resolver.NXDOMAIN:
        raise HTTPException(status_code=404, detail="Domain not found")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
