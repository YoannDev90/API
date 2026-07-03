import asyncio
import json
import os
import re
import urllib.parse

import httpx
from starlette.responses import Response
from logging import getLogger

logger = getLogger("api-proxy")

_USER_AGENTS = None
_RE_ATTR = re.compile(r'(\s(?:href|src|action|data-src)=["\'])([^"\']+)')
_RE_CSS = re.compile(r'(url\(["\']?)(https?://[^"\'\)\s]+)')


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


def _encode_url(url: str) -> str:
    return urllib.parse.quote(url, safe="")


def _rewrite_html(html: str, original_url: str) -> str:
    parsed = urllib.parse.urlparse(original_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    def _rewrite(m):
        attr = m.group(1)
        url = m.group(2)
        if url.startswith("//"):
            url = parsed.scheme + ":" + url
        elif url.startswith("/"):
            url = origin + url
        if url.startswith(("http://", "https://")):
            return f'{attr}"/proxy/{_encode_url(url)}"'
        return m.group(0)

    html = _RE_ATTR.sub(_rewrite, html)
    html = _RE_CSS.sub(lambda m: m.group(1) + "/proxy/" + _encode_url(m.group(2)), html)
    return html


async def proxy_request(request, path: str = "", target_url: str = None, user_agent: str = None):
    if target_url is None:
        raise ValueError("target_url is required")

    qs = request.url.query
    if qs:
        params = urllib.parse.parse_qs(qs)
        params.pop("ua", None)
        params.pop("debug", None)
        if params:
            target_url += "?" + urllib.parse.urlencode(params, doseq=True)

    logger.info(f"Proxy: {request.method} {target_url}")

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

        resp_content = resp.content
        resp_headers = dict(resp.headers)
        resp_status = resp.status_code
        resp_is_html = "text/html" in resp_headers.get("content-type", "")

        if resp_status == 403 and resp_headers.get("cf-mitigated") == "challenge":
            logger.info(f"Cloudflare challenge for {target_url}, retrying with cloudscraper")
            try:
                import cloudscraper
                scraper = cloudscraper.create_scraper()
                cf_resp = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: scraper.get(target_url, headers=headers, timeout=30, allow_redirects=True),
                )
                resp_content = cf_resp.content
                resp_headers = dict(cf_resp.headers)
                resp_status = cf_resp.status_code
                resp_is_html = "text/html" in resp_headers.get("content-type", "")
                logger.info(f"cloudscraper result: {resp_status}")
            except Exception as e:
                logger.error(f"cloudscraper failed: {e}")

        if resp_is_html and resp_content:
            try:
                html = resp_content.decode("utf-8", errors="replace")
                rewritten = _rewrite_html(html, target_url)
                resp_content = rewritten.encode("utf-8")
            except Exception as e:
                logger.warning(f"HTML rewrite failed: {e}")

        proxied_headers = {
            k: v
            for k, v in resp_headers.items()
            if k.lower()
            not in ("x-frame-options", "content-security-policy", "frame-options",
                    "content-encoding", "transfer-encoding", "content-length", "alt-svc")
        }

        is_debug = request.headers.get("x-proxy-debug") == "true"
        if is_debug:
            proxied_headers["x-proxy-status"] = str(resp_status)
            proxied_headers["x-proxy-ua"] = ua
            resp_history = getattr(resp, "history", [])
            proxied_headers["x-proxy-redirects"] = str(len(resp_history))
            if resp_history:
                chain = " -> ".join(str(r.status_code) + " " + str(r.url) for r in resp_history)
                chain += " -> " + str(resp_status) + " " + str(resp.url) if hasattr(resp, "url") else ""
                proxied_headers["x-proxy-redirect-chain"] = chain
            if hasattr(resp, "url"):
                proxied_headers["x-proxy-final-url"] = str(resp.url)
            proxied_headers["x-proxy-content-type"] = resp_headers.get("content-type", "")

        return Response(
            content=resp_content,
            status_code=resp_status,
            headers=proxied_headers,
            media_type=resp_headers.get("content-type"),
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout proxying to {target_url}")
        return Response(b'{"code": "504", "message": "Gateway Timeout"}', status_code=504, media_type="application/json")
    except httpx.ConnectError:
        logger.error(f"Connection error proxying to {target_url}")
        return Response(b'{"code": "502", "message": "Bad Gateway"}', status_code=502, media_type="application/json")
    except Exception as e:
        logger.error(f"Proxy error for {target_url}: {e}")
        return Response(b'{"code": "500", "message": "Internal Server Error"}', status_code=500, media_type="application/json")
