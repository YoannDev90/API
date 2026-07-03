from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import random, re

@router.get("/dice", tags=["tools"])
async def dice_roller(roll: str = Query(default="1d6", description="Dice notation (e.g. 2d6)")):
    m = re.match(r"^(\d+)d(\d+)(?:\+(\d+))?$", roll.lower())
    if not m: raise HTTPException(status_code=400, detail="Invalid dice notation")
    count, sides, bonus = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if count < 1 or count > 100 or sides < 2 or sides > 1000:
        raise HTTPException(status_code=400, detail="Count must be 1-100, sides 2-1000")
    rolls = [random.randint(1, sides) for _ in range(count)]
    return {"code": "200", "notation": roll, "rolls": rolls, "subtotal": sum(rolls), "bonus": bonus, "total": sum(rolls)+bonus}

