from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional

router = APIRouter()

@router.post("/image/generate", tags=["image"])
async def generate_image(
    prompt: str = Form(...),
    model: Optional[str] = Form("flux"),
    size: Optional[str] = Form("1024x1024"),
    format: Optional[str] = Form("base64"),
    enhance: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    api_key: Optional[str] = Depends(lambda: None)
):
    """
    Générer une image à partir d'une description textuelle.
    
    - **prompt**: Description de l'image à générer (obligatoire)
    - **model**: Modèle à utiliser (par défaut: flux)
    - **size**: Taille de l'image (par défaut: 1024x1024)
    - **format**: Format de sortie (par défaut: base64)
    - **enhance**: Amélioration automatique du prompt (par défaut: true)
    - **image**: Image optionnelle pour le context (optionnel)
    """
    pass