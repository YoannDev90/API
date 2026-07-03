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


@router.get("/qr", tags=["utils"])
async def qr_code(text: str = Query(..., description="Text to encode"),
                  size: int = Query(default=300, ge=50, le=2000)):
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.make(text)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        png = buf.getvalue()
        return Response(content=png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"QR failed: {e}")


class MarkdownInput(BaseModel):
    text: str = Field(..., description="Markdown content")


@router.post("/markdown", tags=["utils"])
async def markdown_to_html(body: MarkdownInput):
    try:
        import markdown as md
        html = md.markdown(body.text, extensions=["fenced_code", "tables"])
        return {"code": "200", "html": html}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Markdown failed: {e}")


class ColorInput(BaseModel):
    value: str = Field(..., description="Color: hex (#ff0000), rgb(255,0,0), hsl(0,100,50)")


@router.post("/color", tags=["utils"])
async def color_convert(body: ColorInput):
    import re
    v = body.value.strip().lower()
    try:
        if v.startswith("#"):
            h = v.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        elif v.startswith("rgb"):
            r, g, b = map(int, re.findall(r"\d+", v)[:3])
        elif v.startswith("hsl"):
            h, s, l = map(float, re.findall(r"[\d.]+", v)[:3])
            s /= 100; l /= 100
            c = (1 - abs(2*l - 1)) * s
            x = c * (1 - abs((h/60) % 2 - 1))
            m = l - c/2
            if h < 60: r, g, b = c, x, 0
            elif h < 120: r, g, b = x, c, 0
            elif h < 180: r, g, b = 0, c, x
            elif h < 240: r, g, b = 0, x, c
            elif h < 300: r, g, b = x, 0, c
            else: r, g, b = c, 0, x
            r, g, b = int((r+m)*255), int((g+m)*255), int((b+m)*255)
        else:
            raise ValueError(f"Unsupported format: {v}")
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        r2, g2, b2 = r/255, g/255, b/255
        mx, mn = max(r2, g2, b2), min(r2, g2, b2)
        l2 = (mx + mn) / 2
        if mx == mn: h2, s2 = 0, 0
        else:
            d = mx - mn
            s2 = d / (1 - abs(2*l2 - 1))
            if mx == r2: h2 = 60 * (((g2-b2)/d) % 6)
            elif mx == g2: h2 = 60 * (((b2-r2)/d) + 2)
            else: h2 = 60 * (((r2-g2)/d) + 4)
        return {
            "code": "200",
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "rgb": {"r": r, "g": g, "b": b},
            "hsl": {"h": round(h2, 1), "s": round(s2*100, 1), "l": round(l2*100, 1)},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Color error: {e}")


@router.get("/text-stats", tags=["utils"])
async def text_stats(text: str = Query(..., description="Text to analyze")):
    words = text.split()
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    lines = text.count("\n") + 1
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    return {
        "code": "200",
        "characters": chars,
        "characters_no_space": chars_no_space,
        "words": len(words),
        "lines": lines,
        "sentences": sentences,
        "avg_word_length": round(sum(len(w) for w in words) / max(1, len(words)), 1),
    }


@router.get("/cron", tags=["utils"])
async def cron_explain(expr: str = Query(..., description="Cron expression (e.g. '*/5 * * * *')")):
    try:
        from croniter import croniter
        import datetime
        now = datetime.datetime.now()
        cron = croniter(expr, now)
        next5 = [cron.get_next(datetime.datetime) for _ in range(5)]
        prev = croniter(expr, now).get_prev(datetime.datetime)
        return {
            "code": "200",
            "expression": expr,
            "previous_run": prev.isoformat(),
            "next_5_runs": [d.isoformat() for d in next5],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron: {e}")


class JWTInput(BaseModel):
    token: str = Field(..., description="JWT token")


@router.post("/jwt/decode", tags=["utils"])
async def jwt_decode(body: JWTInput):
    try:
        import jwt
        header = jwt.get_unverified_header(body.token)
        payload = jwt.decode(body.token, options={"verify_signature": False})
        return {"code": "200", "header": header, "payload": payload}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JWT decode failed: {e}")


@router.get("/phone", tags=["utils"])
async def phone_info(number: str = Query(..., description="Phone number with country code (e.g. +33612345678)")):
    try:
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone
        n = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(n):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        return {
            "code": "200",
            "number": phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country": geocoder.description_for_number(n, "en"),
            "carrier": carrier.name_for_number(n, "en"),
            "timezones": timezone.time_zones_for_number(n),
            "type": "mobile" if phonenumbers.number_type(n) == phonenumbers.PhoneNumberType.MOBILE else "fixed_line",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Phone error: {e}")


@router.get("/country", tags=["utils"])
async def country_info(code: str = Query(..., description="ISO country code (e.g. FR, US, JP)")):
    try:
        import pycountry
        c = pycountry.countries.get(alpha_2=code.upper())
        if not c:
            c = pycountry.countries.get(alpha_3=code.upper())
        if not c:
            c = pycountry.countries.get(name=code.title())
        if not c:
            raise HTTPException(status_code=404, detail="Country not found")
        data = {"code": "200", "name": c.name, "alpha_2": c.alpha_2, "alpha_3": c.alpha_3}
        if hasattr(c, "numeric"): data["numeric"] = c.numeric
        if hasattr(c, "official_name"): data["official_name"] = c.official_name
        try:
            sub = pycountry.subdivisions.get(country_code=c.alpha_2)
            if sub: data["subdivisions"] = [s.name for s in pycountry.subdivisions.get(country_code=c.alpha_2)[:20]]
        except Exception:
            pass
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Country error: {e}")


class RegexTestInput(BaseModel):
    pattern: str = Field(..., description="Regex pattern")
    text: str = Field(..., description="Text to test against")
    flags: str = Field(default="", description="Flags: i=ignore case, m=multiline, s=dotall")


@router.post("/regex/test", tags=["utils"])
async def regex_test(body: RegexTestInput):
    try:
        import re
        flags = 0
        if "i" in body.flags: flags |= re.IGNORECASE
        if "m" in body.flags: flags |= re.MULTILINE
        if "s" in body.flags: flags |= re.DOTALL
        compiled = re.compile(body.pattern, flags)
        matches = compiled.findall(body.text)
        return {
            "code": "200",
            "pattern": body.pattern,
            "match_count": len(matches),
            "matches": matches[:100],
            "matched": bool(matches),
        }
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Regex error: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Regex error: {e}")


@router.get("/ssl", tags=["utils"])
async def ssl_check(domain: str = Query(..., description="Domain to check"),
                    port: int = Query(default=443, ge=1, le=65535)):
    try:
        import ssl, socket, datetime
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expire = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                now = datetime.datetime.now()
                days_left = (expire - now).days
                return {
                    "code": "200",
                    "domain": domain,
                    "subject": dict(cert["subject"][0]),
                    "issuer": dict(cert["issuer"][0]),
                    "expires": expire.isoformat(),
                    "days_left": days_left,
                    "expired": days_left < 0,
                    "san": cert.get("subjectAltName", []),
                }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SSL check failed: {e}")


@router.get("/ports", tags=["utils"])
async def port_scan(host: str = Query(..., description="Host to scan"),
                    ports: str = Query(default="22,80,443,8080", description="Comma-separated ports")):
    try:
        import socket
        port_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
        open_ports = []
        for p in port_list:
            try:
                with socket.create_connection((host, p), timeout=1.5):
                    try:
                        service = socket.getservbyport(p)
                    except Exception:
                        service = "unknown"
                    open_ports.append({"port": p, "service": service})
            except Exception:
                pass
        return {"code": "200", "host": host, "open_ports": open_ports, "total_scanned": len(port_list), "total_open": len(open_ports)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Port scan failed: {e}")


HTTP_STATUS_CODES = {
    100: "Continue", 101: "Switching Protocols", 200: "OK", 201: "Created", 204: "No Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified", 307: "Temporary Redirect",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 408: "Request Timeout", 409: "Conflict", 410: "Gone",
    418: "I'm a Teapot", 422: "Unprocessable Entity", 429: "Too Many Requests",
    500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout",
}


@router.get("/http-status", tags=["utils"])
async def http_status_info(code: int = Query(..., description="HTTP status code", ge=100, le=599)):
    name = HTTP_STATUS_CODES.get(code, "Unknown")
    cat = f"{code // 100}xx"
    cats = {"1xx": "Informational", "2xx": "Success", "3xx": "Redirection", "4xx": "Client Error", "5xx": "Server Error"}
    return {"code": "200", "status_code": code, "name": name, "category": cats.get(cat, "Unknown")}


@router.get("/password-strength", tags=["utils"])
async def password_strength(password: str = Query(..., description="Password to check")):
    try:
        import zxcvbn
        r = zxcvbn.zxcvbn(password)
        return {
            "code": "200",
            "score": r["score"],
            "label": ["very weak", "weak", "fair", "strong", "very strong"][r["score"]],
            "crack_time": r["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
            "feedback": r.get("feedback", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Password check failed: {e}")


@router.get("/user-agent", tags=["utils"])
async def user_agent_parse(ua: str = Query(..., description="User-Agent string")):
    try:
        from user_agents import parse
        p = parse(ua)
        return {
            "code": "200",
            "browser": {"family": p.browser.family, "version": p.browser.version_string},
            "os": {"family": p.os.family, "version": p.os.version_string},
            "device": {"family": p.device.family, "brand": p.device.brand or "", "model": p.device.model or ""},
            "is_mobile": p.is_mobile,
            "is_tablet": p.is_tablet,
            "is_pc": p.is_pc,
            "is_bot": p.is_bot,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"UA parse failed: {e}")

