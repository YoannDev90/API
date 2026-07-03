import base64
import uuid
from logging import getLogger

import whois
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

router = APIRouter()
logger = getLogger("api-proxy")


@router.get("/whois", tags=["utils"])
async def whois_lookup(domain: str = Query(..., description="Domain name to query")):
    try:
        w = whois.whois(domain)
        data = {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": _fmt(w.creation_date),
            "expiration_date": _fmt(w.expiration_date),
            "updated_date": _fmt(w.updated_date),
            "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else None,
            "status": w.status,
            "emails": w.emails,
            "org": w.org,
            "country": w.country,
            "dnssec": w.dnssec,
            "whois_server": w.whois_server,
            "raw": w.text[:4096] if w.text else None,
        }
        data = {k: v for k, v in data.items() if v not in (None, "", [], {}, "N/A")}
        return {"code": "200", "data": data}
    except Exception as e:
        logger.error(f"WHOIS lookup failed for {domain}: {e}")
        raise HTTPException(status_code=502, detail=f"WHOIS lookup failed: {e}")


def _fmt(d):
    if not d:
        return None
    if isinstance(d, list):
        return [str(x) for x in d if x]
    return str(d)


@router.get("/uuid", tags=["utils"])
async def generate_uuid(count: int = Query(default=1, ge=1, le=100, description="Number of UUIDs")):
    return {"code": "200", "uuids": [str(uuid.uuid4()) for _ in range(count)]}


class Base64Input(BaseModel):
    data: str = Field(..., description="String to encode/decode")


@router.post("/base64/encode", tags=["utils"])
async def base64_encode(body: Base64Input):
    encoded = base64.urlsafe_b64encode(body.data.encode()).rstrip(b"=").decode()
    return {"code": "200", "encoded": encoded}


@router.post("/base64/decode", tags=["utils"])
async def base64_decode(body: Base64Input):
    try:
        decoded = base64.urlsafe_b64decode(body.data + "==")
        return {"code": "200", "decoded": decoded.decode()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64: {e}")
