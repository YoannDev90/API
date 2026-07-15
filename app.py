import asyncio
import importlib
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from time import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from __init__ import __version__

logger = logging.getLogger("api-proxy")


def load_endpoints(app: FastAPI):
    endpoints_dir = Path(__file__).parent / "endpoints"
    if not endpoints_dir.exists():
        logger.warning("endpoints/ directory not found")
        return

    files = sorted(
        f
        for f in endpoints_dir.rglob("*.py")
        if f.name != "__init__.py"
    )
    for file in files:
        rel = file.relative_to(endpoints_dir.parent)
        module_name = str(rel.with_suffix("")).replace("/", ".")
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)
                logger.info(f"Loaded: {module_name}")
        except Exception as e:
            logger.error(f"Failed to load {module_name}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.startup_time = time()
    app.openapi_schema = None
    yield


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
