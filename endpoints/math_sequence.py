from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/math/sequence", tags=["math"])
async def math_sequence(first: float = Query(..., description="First term"),
                        diff: float = Query(default=None, description="Common difference (arithmetic)"),
                        ratio: float = Query(default=None, description="Common ratio (geometric)"),
                        count: int = Query(default=10, ge=1, le=100)):
    terms = [first]
    for i in range(1, count):
        if diff is not None: terms.append(terms[-1] + diff)
        elif ratio is not None: terms.append(terms[-1] * ratio)
        else: raise HTTPException(status_code=400, detail="Specify diff or ratio")
    return {"code": "200", "type": "arithmetic" if diff else "geometric", "terms": terms, "sum": round(sum(terms), 6)}
