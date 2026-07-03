from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import subprocess, shlex

@router.get("/net/mtr", tags=["network"])
async def net_mtr(host: str = Query(..., description="Hostname or IP")):
    import shutil
    if not shutil.which("mtr"):
        return {"code": "200", "host": host, "error": "mtr not installed on server", "traceroute": None}
    try:
        result = subprocess.run(["mtr", "-r", "-n", "-c", "1", "--report-wide", host], capture_output=True, text=True, timeout=30)
        return {"code": "200", "host": host, "traceroute": result.stdout}
    except Exception as e:
        return {"code": "200", "host": host, "error": str(e), "traceroute": None}
