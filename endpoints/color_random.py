from logging import getLogger

from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()




import random

@router.get("/color/random", tags=["tools"])
async def random_color():
    r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
    return {"code": "200", "hex": f"#{r:02x}{g:02x}{b:02x}", "rgb": {"r": r, "g": g, "b": b}}

