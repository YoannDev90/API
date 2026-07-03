from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import random

@router.get("/color/palette", tags=["tools"])
async def color_palette(base: str = Query(default=None, description="Base hex color"), count: int = Query(default=5, ge=2, le=20)):
    if base:
        b = base.lstrip("#")
        br, bg, bb = int(b[0:2],16), int(b[2:4],16), int(b[4:6],16)
    else: br, bg, bb = random.randint(0,255), random.randint(0,255), random.randint(0,255)
    pal = []
    for i in range(count):
        t = i/(count-1) if count > 1 else 0.5
        s = t * 60 - 30
        pal.append(f"#{max(0,min(255,int(br+s))):02x}{max(0,min(255,int(bg-s*0.5))):02x}{max(0,min(255,int(bb+s*1.5))):02x}")
    return {"code": "200", "base": f"#{br:02x}{bg:02x}{bb:02x}", "palette": pal}

