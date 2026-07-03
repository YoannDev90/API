from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import ssl, socket, datetime

@router.get("/ssl", tags=["utils"])
async def ssl_check(domain: str = Query(..., description="Domain to check"),
                    port: int = Query(default=443, ge=1, le=65535)):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expire = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                now = datetime.datetime.now()
                days_left = (expire - now).days
                return {
                    "code": "200", "domain": domain,
                    "subject": dict(cert["subject"][0]),
                    "issuer": dict(cert["issuer"][0]),
                    "expires": expire.isoformat(), "days_left": days_left,
                    "expired": days_left < 0,
                    "san": cert.get("subjectAltName", []),
                }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SSL check failed: {e}")

