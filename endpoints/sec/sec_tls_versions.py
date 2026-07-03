from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
import ssl, socket

logger = getLogger("api-proxy")
router = APIRouter()

VERSIONS = [
    ("TLS 1.0", ssl.PROTOCOL_TLSv1),
    ("TLS 1.1", ssl.PROTOCOL_TLSv1_1),
    ("TLS 1.2", ssl.PROTOCOL_TLSv1_2),
    ("TLS 1.3", ssl.PROTOCOL_TLS),
]

@router.get("/sec/tls-versions", tags=["security"])
async def sec_tls_versions(domain: str = Query(..., description="Domain name"),
                           port: int = Query(default=443, ge=1, le=65535)):
    results = []
    for name, proto in VERSIONS:
        try:
            ctx = ssl.SSLContext(proto)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((domain, port), timeout=3) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain):
                    cipher = ctx.session_cipher
                    results.append({"version": name, "supported": True, "cipher": cipher[0] if cipher else None})
        except Exception:
            results.append({"version": name, "supported": False, "cipher": None})
    return {"code": "200", "domain": domain, "results": results}
