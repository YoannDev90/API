from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional

router = APIRouter()

@router.post("/generate", tags=["image"])
async def generate_image(
    prompt: str = Form(...),
    model: Optional[str] = Form("flux"),
    size: Optional[str] = Form("1024x1024"),
    format: Optional[str] = Form("base64"),
    enhance: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    api_key: Optional[str] = Depends(lambda: None)
):
    pass