"""
Configuration de l'application FastAPI pour AlphaLLM
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from logging import getLogger
from collections import defaultdict
from time import time
import threading

logger = getLogger("alphallm-api")


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter les headers de contrôle de cache"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


class ClientIPMiddleware(BaseHTTPMiddleware):
    """Middleware pour récupérer l'IP réelle du client via Cloudflare"""
    
    async def dispatch(self, request: Request, call_next):
        # Chercher l'IP réelle du client (Cloudflare utilise CF-Connecting-IP)
        client_ip = request.headers.get("CF-Connecting-IP") or \
                   request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                   request.headers.get("X-Real-IP") or \
                   (request.client.host if request.client else "unknown")
        
        # Ajouter l'IP réelle au contexte de la requête pour accès dans les endpoints
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
                # Log de l'abus
                logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.url.path} - {request_count} requests in {self.time_window}s")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "code": "429",
                        "message": "Too Many Requests - Rate limit exceeded (5 requests per second)",
                        "retry_after": int(self.time_window)
                    },
                    headers={"Retry-After": str(int(self.time_window))}
                )
            
            # Enregistrer cette requête
            self.request_history[client_ip].append(current_time)
        
        # Log de la requête
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
        
        response = await call_next(request)
        return response

def create_app() -> FastAPI:
    app = FastAPI(
        title="AlphaLLM API",
        description="API pour le projet AlphaLLM",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi-schema"
    )

    # Ajouter les middlewares dans le bon ordre (dernier ajouté = exécuté en premier)
    # Ordre d'exécution: Rate limit → Client IP → Cache Control → CORS → TrustedHost
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
    
    return app