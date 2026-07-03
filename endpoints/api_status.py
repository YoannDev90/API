from logging import getLogger

import httpx
from fastapi import APIRouter
from config import config

router = APIRouter()
logger = getLogger("api")


@router.get("/api/status", tags=["internal-proxy"])
async def status_check():
    try:
        url = f"{config.data.base_url.rstrip('/')}/status"
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            data = (
                resp.json()
                if "application/json" in (resp.headers.get("content-type", ""))
                else resp.text
            )
            return {"code": "200", "service": "API Proxy", "data_service": data}
        return {
            "code": str(resp.status_code),
            "service": "API Proxy",
            "data_service": "Service indisponible",
        }
    except httpx.TimeoutException:
        return {"code": "503", "service": "API Proxy", "data_service": "Timeout"}
    except httpx.ConnectError:
        return {
            "code": "503",
            "service": "API Proxy",
            "data_service": "Service indisponible",
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {"code": "500", "service": "API Proxy", "data_service": "Erreur interne"}
