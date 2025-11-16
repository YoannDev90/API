from fastapi import APIRouter, Depends, Body
from typing import Optional
from pydantic import BaseModel, Field

class SummarizeRequest(BaseModel):
    long_text: str = Field(..., min_length=1, max_length=50000)
    max_length: int = Field(256, ge=10, le=1000)

class ConversationNameRequest(BaseModel):
    messages: str = Field(..., min_length=10)

router = APIRouter()

@router.post("/summarize", tags=["text"])
async def summarize_text(
    request: SummarizeRequest,
    api_key: Optional[str] = Depends(lambda: None)
):
    """Résumer un texte."""
    pass

@router.post("/conv_name", tags=["text"])
async def generate_conversation_name(
    request: ConversationNameRequest,
    api_key: Optional[str] = Depends(lambda: None)
):
    """Générer un titre de conversation."""
    pass