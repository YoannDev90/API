from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


import json
from pydantic import BaseModel, Field

class JSONInput(BaseModel):
    data: str = Field(..., description="JSON to infer schema from")

@router.post("/json/schema", tags=["format"])
async def json_schema(body: JSONInput):
    try:
        obj = json.loads(body.data)

        def infer(v):
            if v is None: return {"type": "null"}
            if isinstance(v, bool): return {"type": "boolean"}
            if isinstance(v, int): return {"type": "integer"}
            if isinstance(v, float): return {"type": "number"}
            if isinstance(v, str): return {"type": "string"}
            if isinstance(v, list):
                items = [infer(x) for x in v]
                return {"type": "array", "items": items[0] if items else {}}
            if isinstance(v, dict):
                return {"type": "object", "properties": {k: infer(v) for k, v in v.items()}}
            return {"type": "unknown"}

        return {"code": "200", "schema": {"$schema": "http://json-schema.org/draft-07/schema#", **infer(obj)}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
