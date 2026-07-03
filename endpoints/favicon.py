from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()


@router.get("/favicon.ico", tags=["assets"], include_in_schema=False)
async def favicon():
    path = Path("favicon.ico")
    if path.exists():
        return FileResponse(
            path,
            media_type="image/x-icon",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    return {"code": "404"}
