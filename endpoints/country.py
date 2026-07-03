from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/country", tags=["utils"])
async def country_info(code: str = Query(..., description="ISO country code (e.g. FR, US)")):
    try:
        import pycountry
        c = pycountry.countries.get(alpha_2=code.upper())
        if not c: c = pycountry.countries.get(alpha_3=code.upper())
        if not c: c = pycountry.countries.get(name=code.title())
        if not c: raise HTTPException(status_code=404, detail="Country not found")
        data = {"code": "200", "name": c.name, "alpha_2": c.alpha_2, "alpha_3": c.alpha_3}
        if hasattr(c, "numeric"): data["numeric"] = c.numeric
        if hasattr(c, "official_name"): data["official_name"] = c.official_name
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Country error: {e}")

