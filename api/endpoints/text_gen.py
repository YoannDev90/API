from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional, List

router = APIRouter()

@router.post("/text/generate", tags=["text"])
async def generate_text(
    prompt: str = Form(...),
    model: Optional[str] = Form("auto"),
    user_id: Optional[int] = Form(None),
    username: Optional[str] = Form(None),
    conv_id: Optional[int] = Form(None),
    incognito: Optional[bool] = Form(False),
    files: Optional[List[UploadFile]] = File(None),
    api_key: Optional[str] = Depends(lambda: None)
):
    pass