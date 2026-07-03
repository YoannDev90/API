from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["general"])
async def health_check():
    return {"code": "200", "status": "healthy", "service": "API Proxy"}
