"""
Point d'entrée pour Azure Function App - AlphaLLM API
Utilise Azure Functions Python v2 avec FastAPI via AsgiFunctionApp
"""

import azure.functions as func
import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from time import time
import threading

# Importer les endpoints
from api.endpoints import main, text_gen, image_gen, image_edit, info, misc, jwt_test

# Configuration du logging
logger = logging.getLogger("alphallm-api")
logger.setLevel(logging.INFO)

# Handler console (Azure Functions affichera les logs dans Application Insights)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class ClientIPMiddleware(BaseHTTPMiddleware):
    """Middleware pour récupérer l'IP réelle du client via Cloudflare"""
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.headers.get("CF-Connecting-IP") or \
                   request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                   request.headers.get("X-Real-IP") or \
                   (request.client.host if request.client else "unknown")
        
        request.scope["client_ip"] = client_ip
        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour limiter les requêtes à 5 req/s par IP"""
    
    def __init__(self, app, max_requests: int = 5, time_window: float = 1.0):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_history = defaultdict(list)
        self.lock = threading.Lock()
        
    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Supprimer les requêtes hors de la fenêtre de temps"""
        cutoff_time = current_time - self.time_window
        self.request_history[client_ip] = [
            req_time for req_time in self.request_history[client_ip]
            if req_time > cutoff_time
        ]
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")
        current_time = time()
        
        with self.lock:
            self._cleanup_old_requests(client_ip, current_time)
            request_count = len(self.request_history[client_ip])
            
            if request_count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path}")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "code": "429",
                        "message": "Too Many Requests - Rate limit exceeded (5 requests per second)",
                        "retry_after": int(self.time_window)
                    },
                    headers={"Retry-After": str(int(self.time_window))}
                )
            
            self.request_history[client_ip].append(current_time)
        
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
        
        response = await call_next(request)
        
        if response.status_code == 404:
            logger.warning(f"Request: {request.method} {request.url.path} from {client_ip} - Response: 404 Not Found")
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter les headers de contrôle de cache"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


def create_app() -> FastAPI:
    """Crée l'application FastAPI avec les middlewares configurés"""
    app = FastAPI(
        title="AlphaLLM API",
        description="API pour le projet AlphaLLM",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi-schema"
    )

    # Ajouter les middlewares dans le bon ordre
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(ClientIPMiddleware)
    app.add_middleware(CacheControlMiddleware)
    
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Inclure les routers des endpoints
    app.include_router(main.router)
    app.include_router(info.router)
    app.include_router(image_gen.router)
    app.include_router(image_edit.router)
    app.include_router(misc.router)
    app.include_router(text_gen.router)
    app.include_router(jwt_test.router)
    
    logger.info("Application démarrée avec succès")
    
    return app


# Créer l'application FastAPI
fast_app = create_app()

# Wrapper Azure Functions
app = func.AsgiFunctionApp(
    app=fast_app,
    http_auth_level=func.AuthLevel.ANONYMOUS
)
