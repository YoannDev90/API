import ipaddress
import socket
import urllib.parse
from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from proxy import proxy_request
from config import config

router = APIRouter()
logger = getLogger("api-proxy")

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
</style>
</head>
<body>
<div class="top">
<input id="url" type="text" placeholder="Enter URL (e.g. https://example.com)" autofocus>
<button id="goBtn">Go</button>
</div>
<iframe id="frame" sandbox="allow-scripts allow-forms allow-popups"></iframe>
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


@router.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    tags=["proxy"],
)
async def catch_all_proxy(request: Request, path: str):
    target_url = urllib.parse.unquote(path)
    if not target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")

    hostname = target_url.split("://")[1].split("/")[0].split(":")[0]
    await _check_ssrf(hostname)

    if config.base_url and target_url.startswith(config.base_url):
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info(f"Proxy: {request.method} -> {target_url}")
    return await proxy_request(request, target_url=target_url)


async def _check_ssrf(hostname: str):
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip is not None:
        if ip.is_private or ip.is_loopback:
            raise HTTPException(403, detail="Access to private/local IPs not allowed")
        return

    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(resolved_ip)
        if ip.is_private or ip.is_loopback:
            raise HTTPException(403, detail="Access to private/local IPs not allowed")
    except socket.gaierror:
        raise HTTPException(400, detail="Hostname could not be resolved")
