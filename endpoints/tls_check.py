from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import ssl, socket, datetime, json

@router.get("/tls", tags=["network"])
async def tls_check(domain: str = Query(..., description="Domain name"),
                    port: int = Query(default=443, ge=1, le=65535)):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                ver = ssock.version()
                cipher = ssock.cipher()
                cert = ssock.getpeercert()
                expire = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                now = datetime.datetime.now()
                return {"code": "200", "domain": domain, "tls_version": ver,
                        "cipher": {"name": cipher[0], "protocol": cipher[1], "bits": cipher[2]},
                        "expires": expire.isoformat(), "days_left": (expire - now).days,
                        "subject": dict(cert["subject"][0]), "issuer": dict(cert["issuer"][0])}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
