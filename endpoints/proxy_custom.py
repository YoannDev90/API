import ipaddress
import socket
from logging import getLogger
from typing import Optional, Dict, Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

router = APIRouter()
logger = getLogger("api-proxy")


class ProxyRequest(BaseModel):
    url: str = Field(..., description="Destination URL")
    method: str = Field(default="GET", description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default=None)
    data: Optional[str] = Field(default=None)
    json_data: Optional[Dict[str, Any]] = Field(default=None)
    timeout: Optional[int] = Field(default=30, ge=1, le=300)


PROXY_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proxy</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#111;color:#eee}
.top{background:#1a1a2e;padding:10px 16px;display:flex;gap:10px;align-items:center;position:sticky;top:0;z-index:99}
.top input{flex:1;padding:8px 12px;border:1px solid #333;border-radius:6px;background:#222;color:#eee;font-size:14px}
.top input:focus{outline:none;border-color:#22c55e}
.top button{padding:8px 20px;background:#22c55e;color:#000;border:none;border-radius:6px;font-weight:600;cursor:pointer}
.top button:hover{background:#16a34a}
iframe{width:100%;height:calc(100vh - 52px);border:none;background:#fff}
.hint{padding:40px;text-align:center;color:#666;font-size:18px}
</style>
</head>
<body>
<div class="top">
<input id="url" type="text" placeholder="Enter URL (e.g. https://example.com)" autofocus>
<button id="goBtn">Go</button>
</div>
<iframe id="frame"></iframe>
<script>
document.addEventListener("DOMContentLoaded",function(){
  var url=document.getElementById("url"),btn=document.getElementById("goBtn"),f=document.getElementById("frame");
  function load(){
    var u=url.value.trim();
    if(!u)return;
    if(!u.startsWith("http://")&&!u.startsWith("https://"))u="https://"+u;
    btn.textContent="...";
    f.src="/proxy/"+encodeURIComponent(u);
  }
  btn.addEventListener("click",load);
  url.addEventListener("keydown",function(e){if(e.key==="Enter")load()});
  f.addEventListener("load",function(){btn.textContent="Go"});
  f.addEventListener("error",function(){btn.textContent="Go"});
});
</script>
</body>
</html>"""


@router.get("/proxy", tags=["proxy"])
async def proxy_ui():
    return Response(content=PROXY_UI, media_type="text/html")


@router.post("/proxy", tags=["proxy"])
async def custom_proxy(proxy_req: ProxyRequest, request: Request):
    client_ip = request.scope.get("client_ip", "unknown")
    logger.info(f"Custom proxy: {proxy_req.method} {proxy_req.url} from {client_ip}")

    if not proxy_req.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400, detail="URL must start with http:// or https://"
        )

    hostname = proxy_req.url.split("://")[1].split("/")[0].split(":")[0]
    await _check_ssrf(hostname)

    try:
        data = proxy_req.json_data or proxy_req.data
        async with httpx.AsyncClient(timeout=proxy_req.timeout) as client:
            resp = await client.request(
                method=proxy_req.method.upper(),
                url=proxy_req.url,
                headers=proxy_req.headers,
                json=data if isinstance(data, dict) else None,
                content=data if isinstance(data, str) else None,
                follow_redirects=False,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway Timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def _check_ssrf(hostname: str):
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip is not None:
        if ip.is_private or ip.is_loopback:
            raise HTTPException(
                status_code=403, detail="Access to private/local IPs not allowed"
            )
        return

    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(resolved_ip)
        if ip.is_private or ip.is_loopback:
            raise HTTPException(
                status_code=403, detail="Access to private/local IPs not allowed"
            )
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Hostname could not be resolved")
