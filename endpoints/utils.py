import base64
import datetime
import hashlib
import json
import os
import secrets
import string
import socket
import uuid
from logging import getLogger

import dns.resolver
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
    if not d: return None
    if isinstance(d, list): return [str(x) for x in d if x]
    return str(d)


@router.get("/uuid", tags=["utils"])
async def generate_uuid(count: int = Query(default=1, ge=1, le=100)):
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
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64")


class TranslateInput(BaseModel):
    text: str = Field(..., description="Text to translate")
    source: str = Field(default="auto")
    target: str = Field(default="en")


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
async def screenshot(url: str = Query(..., description="Website URL")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        from playwright.async_api import async_playwright
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.join(os.path.dirname(__file__), "..", ".pw-browsers"))
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            await page.goto(url, wait_until="networkidle", timeout=30000)
            png = await page.screenshot(type="png", full_page=False)
            await browser.close()
        return Response(content=png, media_type="image/png")
    except Exception as e:
        logger.error(f"Screenshot failed for {url}: {e}")
        raise HTTPException(status_code=502, detail=f"Screenshot failed: {e}")


class HashInput(BaseModel):
    text: str = Field(..., description="Text to hash")


@router.post("/hash", tags=["utils"])
async def hash_text(body: HashInput):
    text = body.text.encode()
    return {
        "code": "200",
        "input": body.text,
        "md5": hashlib.md5(text).hexdigest(),
        "sha1": hashlib.sha1(text).hexdigest(),
        "sha256": hashlib.sha256(text).hexdigest(),
        "sha512": hashlib.sha512(text).hexdigest(),
    }


@router.get("/password", tags=["utils"])
async def password(length: int = Query(default=20, ge=4, le=128)):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pw = "".join(secrets.choice(chars) for _ in range(length))
    return {"code": "200", "length": length, "password": pw}


@router.get("/timestamp", tags=["utils"])
async def timestamp(value: int = Query(description="Unix timestamp in seconds")):
    try:
        dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return {
            "code": "200",
            "unix_seconds": value,
            "iso_8601": dt.isoformat(),
            "utc": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "weekday": dt.strftime("%A"),
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timestamp")


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
