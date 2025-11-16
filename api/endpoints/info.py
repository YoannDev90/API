from fastapi import APIRouter

router = APIRouter()

@router.get("/text-models", tags=["info"])
async def get_text_models():
    """Récupérer la liste des modèles de texte disponibles."""
    pass

@router.get("/image-models", tags=["info"])
async def get_image_models():
    """Récupérer la liste des modèles d'image disponibles."""
    pass