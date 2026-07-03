import sys
from importlib.metadata import version
from fastapi import APIRouter

router = APIRouter()


@router.get("/version", tags=["general"])
async def version_info():
    return {
        "code": "200",
        "version": "2.0.0",
        "python_version": sys.version.split()[0],
        "fastapi_version": version("fastapi"),
    }
