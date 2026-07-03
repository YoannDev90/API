import httpx
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/ip", tags=["general"])
async def client_ip(request: Request):
    client_ip = request.scope.get("client_ip", "unknown")

    forwarded = request.headers.get("X-Forwarded-For", "")
    cf_ip = request.headers.get("CF-Connecting-IP", "")
    real_ip = request.headers.get("X-Real-IP", "")

    geo = None
    try:
        ip_for_lookup = cf_ip or forwarded.split(",")[0].strip() or client_ip
        if ip_for_lookup and ip_for_lookup != "unknown" and ip_for_lookup != "127.0.0.1" and ip_for_lookup != "::1":
            async with httpx.AsyncClient(timeout=3) as c:
                resp = await c.get(f"https://ipinfo.io/{ip_for_lookup}/json")
                if resp.status_code == 200:
                    geo = resp.json()
    except Exception:
        pass

    return {
        "code": "200",
        "client_ip": client_ip,
        "x_forwarded_for": forwarded or None,
        "cf_connecting_ip": cf_ip or None,
        "x_real_ip": real_ip or None,
        "geo": geo,
    }
