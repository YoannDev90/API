from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




UNITS = {
    "length": {"m":1,"km":1000,"cm":0.01,"mm":0.001,"mi":1609.34,"yd":0.9144,"ft":0.3048,"in":0.0254},
    "weight": {"kg":1,"g":0.001,"mg":1e-6,"lb":0.453592,"oz":0.0283495},
    "volume": {"l":1,"ml":0.001,"gal":3.78541,"qt":0.946353,"pt":0.473176,"cup":0.236588,"fl_oz":0.0295735},
}

@router.get("/convert", tags=["tools"])
async def unit_convert(value: float = Query(..., description="Value to convert"),
                       from_: str = Query(alias="from", description="Source unit"),
                       to: str = Query(..., description="Target unit")):
    for cat, units in UNITS.items():
        if from_ in units and to in units:
            return {"code": "200", "category": cat, "value": value, "from": from_, "to": to, "result": round(value * units[from_] / units[to], 6)}
    raise HTTPException(status_code=400, detail=f"Unknown units")

