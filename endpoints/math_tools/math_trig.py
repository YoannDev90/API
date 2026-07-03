from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import math

@router.get("/math/trig", tags=["math"])
async def math_trig(angle: float = Query(..., description="Angle in degrees"),
                    func: str = Query(..., description="sin|cos|tan|asin|acos|atan")):
    rad = math.radians(angle)
    funcs = {"sin": math.sin, "cos": math.cos, "tan": math.tan,
             "asin": lambda x: math.degrees(math.asin(x)), "acos": lambda x: math.degrees(math.acos(x)),
             "atan": lambda x: math.degrees(math.atan(x))}
    if func not in funcs: raise HTTPException(status_code=400, detail=f"Unknown function: {func}")
    rad_val = funcs[func](rad) if func in ("sin", "cos", "tan") else None
    result = funcs[func](angle if func in ("asin", "acos", "atan") else rad)
    return {"code": "200", "function": func, "angle_deg": angle if func in ("asin","acos","atan") else None,
            "angle_rad": round(rad, 6) if func in ("sin","cos","tan") else None, "result": round(result, 6)}
