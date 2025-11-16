from fastapi import APIRouter, Depends, Query
from typing import Optional

router = APIRouter()

@router.get("/summarize", tags=["text"])
async def summarize_text(
    long_text: str = Query(..., min_length=1, max_length=50000),
    max_length: int = Query(256, ge=10, le=1000),
    api_key: Optional[str] = Depends(lambda: None)
):
    """Résumer un texte."""
    pass

@router.get("/conv_name", tags=["text"])
async def generate_conversation_name(
    messages: str = Query(..., min_length=10),
    api_key: Optional[str] = Depends(lambda: None)
):
    """Générer un titre de conversation."""
    pass