import platform
import sys
import time

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/debug", tags=["general"])
async def debug_headers(request: Request):
    client_ip = request.scope.get("client_ip", "unknown")

    headers = dict(request.headers)

    cf_keys = [
        "cf-connecting-ip", "cf-ipcountry", "cf-ipcity", "cf-ipcontinent",
        "cf-iplatitude", "cf-iplongitude", "cf-ippostalcode", "cf-iptimezone",
        "cf-ray", "cf-request-id", "cf-visitor", "cf-tls-version",
        "cf-tls-cipher", "cf-tls-client-auth", "true-client-ip",
        "x-forwarded-for", "x-forwarded-proto", "x-forwarded-host",
    ]
    cf_info = {k.replace("-", "_"): headers.get(k) for k in cf_keys if headers.get(k)}

    query = dict(request.query_params)
    cookies = dict(request.cookies)
    scheme = request.scope.get("scheme", "")
    http_version = request.scope.get("http_version", "")
    server = request.scope.get("server")
    app = request.app

    uptime = None
    if hasattr(app, "startup_time"):
        uptime_secs = time.time() - app.startup_time
        uptime = {
            "seconds": round(uptime_secs, 2),
            "human": f"{int(uptime_secs // 3600)}h {int((uptime_secs % 3600) // 60)}m {int(uptime_secs % 60)}s",
        }

    return {
        "code": "200",
        "message": "Debug HTTP headers",
        "request": {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": query or None,
            "http_version": http_version,
            "scheme": scheme,
            "client_ip_resolved": client_ip,
            "cookies": cookies or None,
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
            "server": {"host": server[0], "port": server[1]} if server else None,
        },
        "cloudflare_info": cf_info or None,
        "all_headers": headers,
        "server_info": {
            "version": getattr(app, "version", ""),
            "uptime": uptime,
            "routes_count": len([r for r in app.routes if hasattr(r, "path")]),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.system(),
            "platform_release": platform.release(),
        },
    }
