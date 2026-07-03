import json
import os
from urllib.parse import parse_qs, urlencode

import httpx
from starlette.responses import Response
from logging import getLogger
from config import config

logger = getLogger("api-proxy")

_USER_AGENTS = None


def _load_uas():
    global _USER_AGENTS
    if _USER_AGENTS is not None:
        return _USER_AGENTS
    path = os.path.join(os.path.dirname(__file__), "user_agents.json")
    try:
        with open(path) as f:
            _USER_AGENTS = json.load(f)
    except Exception:
        _USER_AGENTS = {"Default": "API-Proxy/1.0"}
    return _USER_AGENTS


async def proxy_request(request, path: str = "", target_url: str = None, user_agent: str = None):
    if target_url is None:
        target_url = f"{config.base_url.rstrip('/')}/{path}"

    qs = request.url.query
    if qs:
        params = parse_qs(qs)
        params.pop("ua", None)
        params.pop("debug", None)
        if params:
            target_url += "?" + urlencode(params, doseq=True)

    client_ip = request.scope.get("client_ip", "unknown")
    logger.info(f"Proxy: {request.method} {target_url} from {client_ip}")

    try:
        body = await request.body()
        ua = user_agent or "API-Proxy/1.0"
        headers = {"user-agent": ua, "accept": "*/*"}
        if body:
            headers["content-type"] = "application/octet-stream"

        async with httpx.AsyncClient(timeout=30.0, max_redirects=10) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=True,
            )
            proxied_headers = {
                k: v
                for k, v in resp.headers.items()
                if k.lower()
                not in (
                    "x-frame-options",
                    "content-security-policy",
                    "frame-options",
                    "content-encoding",
                    "transfer-encoding",
                    "content-length",
                    "alt-svc",
                )
            }

            is_debug = request.headers.get("x-proxy-debug") == "true"
            if is_debug:
                proxied_headers["x-proxy-status"] = str(resp.status_code)
                proxied_headers["x-proxy-ua"] = ua
                proxied_headers["x-proxy-redirects"] = str(len(resp.history))
                if resp.history:
                    redirect_chain = " -> ".join(str(r.status_code) + " " + str(r.url) for r in resp.history)
                    redirect_chain += " -> " + str(resp.status_code) + " " + str(resp.url)
                    proxied_headers["x-proxy-redirect-chain"] = redirect_chain
                proxied_headers["x-proxy-final-url"] = str(resp.url)
                proxied_headers["x-proxy-content-type"] = resp.headers.get("content-type", "")

            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=proxied_headers,
                media_type=resp.headers.get("content-type"),
            )
    except httpx.TimeoutException:
        logger.error(f"Timeout proxying to {target_url}")
        return Response(
            b'{"code": "504", "message": "Gateway Timeout"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        logger.error(f"Connection error proxying to {target_url}")
        return Response(
            b'{"code": "502", "message": "Bad Gateway"}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Proxy error for {target_url}: {e}")
        return Response(
            b'{"code": "500", "message": "Internal Server Error"}',
            status_code=500,
            media_type="application/json",
        )
