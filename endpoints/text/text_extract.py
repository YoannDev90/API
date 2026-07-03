from logging import getLogger
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import re

logger = getLogger("api-proxy")
router = APIRouter()


class TextInput(BaseModel):
    text: str = Field(..., description="Input text")


@router.post("/text/extract", tags=["text"])
async def text_extract(body: TextInput):
    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body.text)))
    urls = list(set(re.findall(r'https?://[^\s<>]+', body.text)))
    ips = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', body.text)))
    phones = list(set(re.findall(r'\+?\d[\d\s.-]{7,15}\d', body.text)))
    return {"code": "200", "extracted": {"emails": emails, "urls": urls, "ips": ips, "phones": phones}}
