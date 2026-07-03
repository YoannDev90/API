import asyncio
import importlib
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from time import time

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import config, allowed_proxy_paths
from keep_alive import start_self_ping
from __init__ import __version__

logger = logging.getLogger("api-proxy")


def load_endpoints(app: FastAPI):
    endpoints_dir = Path(__file__).parent / "endpoints"
    if not endpoints_dir.exists():
        logger.warning("endpoints/ directory not found")
        return

    files = sorted(
        f
        for f in endpoints_dir.glob("*.py")
        if f.name not in ("__init__.py", "api_catchall.py")
    )
    for file in files:
        module_name = f"endpoints.{file.stem}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)
                logger.info(f"Loaded: {module_name}")
        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")

    try:
        module = importlib.import_module("endpoints.api_catchall")
        if hasattr(module, "router"):
            app.include_router(module.router)
            logger.info("Loaded: endpoints.api_catchall")
    except Exception as e:
        logger.error(f"Failed to load endpoints.api_catchall: {e}")


async def load_allowed_paths(app: FastAPI):
    logger.info("Loading allowed paths from upstream...")
    try:
        schema_url = f"{config.base_url.rstrip('/')}/openapi.json"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(schema_url)
        if resp.status_code == 200:
            schema = resp.json()
            paths = schema.get("paths", {})
            app.origin_schema = schema
            for path in paths:
                normalized = path.split("{")[0].rstrip("/")
                if normalized and normalized not in ("", "/", "/status", "/resources"):
                    allowed_proxy_paths.add(normalized)
            logger.info(f"Allowed paths: {sorted(allowed_proxy_paths)}")
        else:
            logger.warning(f"OpenAPI schema load failed: {resp.status_code}")
    except Exception as e:
        logger.error(f"OpenAPI schema error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_allowed_paths(app)
    ping_task = await start_self_ping()
    app.startup_time = time()
    app.openapi_schema = None
    yield
    if ping_task:
        ping_task.cancel()


class ClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip = (
            request.headers.get("CF-Connecting-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.headers.get("X-Real-IP")
            or (request.client.host if request.client else "unknown")
        )
        request.scope["client_ip"] = client_ip
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.history = defaultdict(list)
        self.lock = asyncio.Lock()

    _MAX_REQ = 5
    _WINDOW = 1.0

    async def dispatch(self, request, call_next):
        client_ip = request.scope.get("client_ip", "unknown")
        path = request.url.path
        max_req, window = self._MAX_REQ, self._WINDOW
        key = f"{client_ip}:{path}"

        async with self.lock:
            cutoff = time() - window
            recent = [t for t in self.history[key] if t > cutoff]
            if len(recent) >= max_req:
                return JSONResponse(
                    status_code=429,
                    content={
                        "code": "429",
                        "message": f"Rate limit exceeded ({max_req} req/s)",
                    },
                    headers={"Retry-After": str(int(window))},
                )
            recent.append(time())
            self.history[key] = recent

        return await call_next(request)


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Proxy",
        description="API Proxy",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(ClientIPMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        allow_headers=["*"],
    )

    load_endpoints(app)
    logger.info("Application started")
    return app


app = create_app()
