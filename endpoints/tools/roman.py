from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/roman", tags=["tools"])
async def roman_numeral(value: str = Query(..., description="Number or Roman numeral"),
                        direction: str = Query(default="to_roman", description="to_roman or to_number")):
    if direction == "to_roman":
        try:
            n = int(value)
            if n < 1 or n > 3999: raise HTTPException(status_code=400, detail="Number must be 1-3999")
            vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
            r = ""
            for v, s in vals:
                while n >= v: r += s; n -= v
            return {"code": "200", "number": value, "roman": r}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid number")
    else:
        v = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
        try:
            r, p = 0, 0
            for c in value.upper()[::-1]:
                cv = v[c]
                if cv < p: r -= cv
                else: r += cv
                p = cv
            return {"code": "200", "roman": value, "number": r}
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Roman numeral")

