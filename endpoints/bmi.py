from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/bmi", tags=["tools"])
async def bmi_calculator(weight: float = Query(..., description="Weight in kg", gt=0),
                         height: float = Query(..., description="Height in cm", gt=0)):
    bmi = round(weight / ((height / 100) ** 2), 2)
    cat = "underweight" if bmi < 18.5 else "healthy" if bmi < 25 else "overweight" if bmi < 30 else "obese"
    return {"code": "200", "weight_kg": weight, "height_cm": height, "bmi": bmi, "category": cat}

