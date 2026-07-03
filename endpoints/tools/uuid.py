from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/uuid", tags=["utils"])
async def generate_uuid(count: int = Query(default=1, ge=1, le=100)):
    import uuid
    return {"code": "200", "uuids": [str(uuid.uuid4()) for _ in range(count)]}

