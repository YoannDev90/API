from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import re as _re

class ColorInput(BaseModel):
    value: str = Field(..., description="Color: hex (#ff0000), rgb(255,0,0), hsl(0,100,50)")

@router.post("/color", tags=["utils"])
async def color_convert(body: ColorInput):
    v = body.value.strip().lower()
    try:
        if v.startswith("#"):
            h = v.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        elif v.startswith("rgb"):
            r, g, b = map(int, _re.findall(r"\d+", v)[:3])
        elif v.startswith("hsl"):
            h, s, l = map(float, _re.findall(r"[\d.]+", v)[:3])
            s /= 100; l /= 100
            c = (1 - abs(2*l - 1)) * s
            x = c * (1 - abs((h/60) % 2 - 1))
            m = l - c/2
            if h < 60: r, g, b = c, x, 0
            elif h < 120: r, g, b = x, c, 0
            elif h < 180: r, g, b = 0, c, x
            elif h < 240: r, g, b = 0, x, c
            elif h < 300: r, g, b = x, 0, c
            else: r, g, b = c, 0, x
            r, g, b = int((r+m)*255), int((g+m)*255), int((b+m)*255)
        else:
            raise ValueError()
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        r2, g2, b2 = r/255, g/255, b/255
        mx, mn = max(r2, g2, b2), min(r2, g2, b2)
        l2 = (mx + mn) / 2
        if mx == mn: h2, s2 = 0, 0
        else:
            d = mx - mn
            s2 = d / (1 - abs(2*l2 - 1))
            if mx == r2: h2 = 60 * (((g2-b2)/d) % 6)
            elif mx == g2: h2 = 60 * (((b2-r2)/d) + 2)
            else: h2 = 60 * (((r2-g2)/d) + 4)
        return {
            "code": "200",
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "rgb": {"r": r, "g": g, "b": b},
            "hsl": {"h": round(h2, 1), "s": round(s2*100, 1), "l": round(l2*100, 1)},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Color error: {e}")

