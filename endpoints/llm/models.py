"""Pydantic models matching OpenAI API schema."""
from typing import Optional, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="system, user, assistant")
    content: str | list | None = None
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="auto", description="Model name or 'auto' for best available")
    messages: list[Message] = Field(..., min_length=1)
    stream: Optional[bool] = False
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=131072)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    stop: Optional[str | list[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None


class EmbeddingRequest(BaseModel):
    model: str = Field(default="text-embedding-3-small")
    input: str | list[str] = Field(...)
    dimensions: Optional[int] = None


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(...)
    model: Optional[str] = None
    size: Optional[str] = None
    n: Optional[int] = 1


class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[dict]


class ProviderStatus(BaseModel):
    name: str
    enabled: bool
    latency_ms: float
    successes: int
    errors: int
    available_models: list[str]
    supports_stream: bool
