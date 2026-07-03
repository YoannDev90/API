from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


import json
from pydantic import BaseModel, Field

class PatchInput(BaseModel):
    document: dict = Field(..., description="JSON document")
    patch: list = Field(..., description="JSON Patch (RFC 6902)")

@router.post("/json/patch", tags=["format"])
async def json_patch(body: PatchInput):
    try:
        doc = body.document
        for op in body.patch:
            parts = op["path"].strip("/").split("/")
            target = doc
            for p in parts[:-1]:
                if isinstance(target, dict): target = target.get(p, {})
                elif isinstance(target, list): target = target[int(p)]
            key = parts[-1] if parts else None
            if op["op"] == "replace" or op["op"] == "add":
                if isinstance(target, dict) and key: target[key] = op["value"]
                elif isinstance(target, list): target[int(key)] = op["value"]
            elif op["op"] == "remove":
                if isinstance(target, dict) and key: del target[key]
                elif isinstance(target, list): del target[int(key)]
        return {"code": "200", "result": doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
