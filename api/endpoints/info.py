from fastapi import APIRouter, Request
from api.utils.models_utils import load_models_data

router = APIRouter()

@router.get("/text-models", tags=["info"])
async def get_text_models():
    """Récupérer la liste des modèles de texte disponibles."""
    models = load_models_data("text")
    return {
        "type": "text",
        "models": models
    }

@router.get("/image-models", tags=["info"])
async def get_image_models():
    """Récupérer la liste des modèles d'image disponibles."""
    models = load_models_data("image")
    return {
        "type": "image",
        "models": models
    }

@router.get("/endpoints", tags=["info"])
async def get_endpoints(request: Request):
    """Récupérer la liste de tous les endpoints disponibles."""
    app = request.app
    endpoints = []
    
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            if not route.path.startswith("/openapi") and not route.path.startswith("/docs") and not route.path.startswith("/redoc"):
                endpoint_info = {
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "tags": route.tags if hasattr(route, "tags") else [],
                    "description": route.summary or route.description or ""
                }
                endpoints.append(endpoint_info)
    
    return {
        "total": len(endpoints),
        "endpoints": endpoints
    }
