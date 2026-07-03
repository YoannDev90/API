from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import ssl, socket

@router.get("/net/cert-chain", tags=["network"])
async def net_cert_chain(domain: str = Query(..., description="Domain name"),
                         port: int = Query(default=443, ge=1, le=65535)):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                chain = ssock.get_unverified_chain()
                certs = []
                for c in chain:
                    from cryptography import x509
                    from cryptography.hazmat.backends import default_backend
                    cert = x509.load_der_x509_certificate(c, default_backend())
                    certs.append({
                        "subject": str(cert.subject.rfc4514_string()),
                        "issuer": str(cert.issuer.rfc4514_string()),
                        "serial": str(cert.serial_number),
                        "not_before": str(cert.not_valid_before),
                        "not_after": str(cert.not_valid_after),
                    })
                return {"code": "200", "domain": domain, "cert_chain": certs, "depth": len(certs)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
