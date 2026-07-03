from fastapi import APIRouter, Request
from logging import getLogger

router = APIRouter()
logger = getLogger("api")


@router.get("/debug", tags=["general"])
async def debug_headers(request: Request):
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")
    headers = dict(request.headers)

    cf_keys = [
        "cf-connecting-ip", "cf-ipcountry", "cf-ipcity", "cf-ipcontinent",
        "cf-iplatitude", "cf-iplongitude", "cf-ippostalcode", "cf-iptimezone",
        "cf-ray", "cf-request-id", "cf-visitor", "cf-tls-version",
        "cf-tls-cipher", "cf-tls-client-auth", "true-client-ip",
        "x-forwarded-for", "x-forwarded-proto", "x-forwarded-host",
    ]
    cloudflare_info = {k.replace("-", "_"): headers.get(k, "N/A") for k in cf_keys}
    cloudflare_info = {k: v for k, v in cloudflare_info.items() if v != "N/A"}

    return {
        "code": "200",
        "message": "Debug - En-têtes HTTP",
        "client_ip_resolved": client_ip,
        "cloudflare_info": cloudflare_info or "Aucune info Cloudflare détectée",
        "all_headers": headers,
    }
