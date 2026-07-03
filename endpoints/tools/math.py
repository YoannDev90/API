from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import re as _re

@router.get("/math", tags=["tools"])
async def math_eval(expr: str = Query(..., description="Math expression (e.g. 2+2*3)")):
    if not _re.match(r"^[\d\s+\-*/().,%^]+$", expr):
        raise HTTPException(status_code=400, detail="Expression contains invalid characters")
    try:
        return {"code": "200", "expression": expr, "result": eval(expr, {"__builtins__": {}}, {})}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Math error: {e}")

