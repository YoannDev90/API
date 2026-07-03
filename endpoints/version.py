import sys
from importlib.metadata import version
from fastapi import APIRouter
from __init__ import __version__

router = APIRouter()


@router.get("/version", tags=["general"])
async def version_info():
    return {
        "code": "200",
        "version": __version__,
        "python_version": sys.version.split()[0],
        "fastapi_version": version("fastapi"),
    }
