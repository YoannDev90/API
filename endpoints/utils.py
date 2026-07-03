import base64
import os
import uuid
from logging import getLogger

import httpx
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


class TranslateInput(BaseModel):
    text: str = Field(..., description="Text to translate")
    source: str = Field(default="auto", description="Source language (e.g. 'en', 'fr', 'auto')")
    target: str = Field(default="en", description="Target language (e.g. 'en', 'fr')")


@router.post("/translate", tags=["utils"])
async def translate(body: TranslateInput):
    try:
        from deep_translator import GoogleTranslator
        t = GoogleTranslator(source=body.source, target=body.target)
        result = t.translate(body.text)
        return {"code": "200", "source": body.source, "target": body.target, "text": body.text, "translated": result}
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=502, detail=f"Translation failed: {e}")


@router.get("/screenshot", tags=["utils"])
async def screenshot(url: str = Query(..., description="Website URL to screenshot")):
    api_url = os.getenv("SCREENSHOT_API_URL", "")
    api_key = os.getenv("SCREENSHOT_API_KEY", "")

    if api_url and api_key:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                params = {"key": api_key, "url": url, "device": "desktop"}
                if "{url}" in api_url:
                    target = api_url.replace("{url}", url)
                else:
                    target = api_url
                resp = await client.get(target, params=params if "?" not in target else None)
                return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/png"))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Screenshot failed: {e}")

    raise HTTPException(status_code=501, detail="Screenshot not configured. Set SCREENSHOT_API_URL and SCREENSHOT_API_KEY")
