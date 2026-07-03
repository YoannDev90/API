from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import re

@router.get("/slugify", tags=["tools"])
async def slugify(text: str = Query(..., description="Text to slugify"), separator: str = Query(default="-")):
    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower().strip())
    slug = re.sub(r"[\s-]+", separator, slug).strip(separator)
    return {"code": "200", "original": text, "slug": slug}

