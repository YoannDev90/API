from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import json
from fastapi.responses import Response

class JSONInput(BaseModel):
    data: str = Field(..., description="JSON string")

@router.post("/json/format", tags=["tools"])
async def json_format(body: JSONInput):
    try:
        parsed = json.loads(body.data)
        return Response(content=json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

