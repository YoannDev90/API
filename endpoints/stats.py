from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from collections import Counter

@router.get("/stats", tags=["tools"])
async def statistics(values: str = Query(..., description="Comma-separated numbers")):
    nums = [float(x.strip()) for x in values.split(",")]
    n = len(nums); s = sum(nums); mn = s / n
    sn = sorted(nums)
    med = sn[n//2] if n % 2 else (sn[n//2-1]+sn[n//2])/2
    c = Counter(nums)
    var = sum((x-mn)**2 for x in nums) / (n-1) if n > 1 else 0
    return {"code": "200", "count": n, "sum": s, "min": min(nums), "max": max(nums), "mean": round(mn,4),
            "median": round(med,4), "mode": [k for k,v in c.items() if v==max(c.values())],
            "variance": round(var,4), "stddev": round(var**0.5,4)}

