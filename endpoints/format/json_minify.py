from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import json
from fastapi.responses import Response

class JSONInput(BaseModel):
    data: str = Field(..., description="JSON string")

@router.post("/json/minify", tags=["tools"])
async def json_minify(body: JSONInput):
    try:
        parsed = json.loads(body.data)
        return Response(content=json.dumps(parsed, separators=(",",":"), ensure_ascii=False), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

