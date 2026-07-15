"""Slim API: LLM endpoints only (for Waifly 300MB)."""
import importlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from __init__ import __version__

logger = logging.getLogger("api-proxy")


def load_llm_endpoints(app: FastAPI):
    """Load only LLM endpoints."""
    module = importlib.import_module("endpoints.llm.api")
    if hasattr(module, "router"):
        app.include_router(module.router)
        logger.info("Loaded: endpoints.llm.api")


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
        self.history = {}
        self.lock = None

    _MAX_REQ = 5
    _WINDOW = 1.0

    async def dispatch(self, request, call_next):
        import asyncio
        if self.lock is None:
            self.lock = asyncio.Lock()

        client_ip = request.scope.get("client_ip", "unknown")
        path = request.url.path
        max_req, window = self._MAX_REQ, self._WINDOW
        key = f"{client_ip}:{path}"

        async with self.lock:
            from collections import defaultdict
            cutoff = time() - window
            recent = [t for t in self.history.get(key, []) if t > cutoff]
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


def create_app() -> FastAPI:
    app = FastAPI(
        title="LLM API",
        description="Free LLM API (OpenAI-compatible)",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(ClientIPMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    load_llm_endpoints(app)
    logger.info("LLM API started")
    return app


app = create_app()