from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", tags=["general"])
async def ping():
    return {"code": "200", "message": "pong"}
