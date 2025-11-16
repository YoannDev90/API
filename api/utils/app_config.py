"""
Configuration de l'application FastAPI pour AlphaLLM
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


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

def create_app() -> FastAPI:
    app = FastAPI(
        title="AlphaLLM API",
        description="API pour le projet AlphaLLM",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Ajouter les middlewares dans le bon ordre (dernier ajouté = exécuté en premier)
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