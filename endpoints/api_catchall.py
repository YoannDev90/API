from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from config import allowed_proxy_paths
from proxy import proxy_request

router = APIRouter()
logger = getLogger("api")


@router.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    tags=["internal-proxy"],
    include_in_schema=False,
)
async def api_proxy_catch_all(request: Request, path: str):
    if not allowed_proxy_paths:
        raise HTTPException(
            status_code=503, detail="Service not ready - schema not loaded"
        )

    request_path = f"/{path}"
    if not any(request_path.startswith(allowed) for allowed in allowed_proxy_paths):
        raise HTTPException(status_code=404, detail="Not Found")

    response = await proxy_request(request, path)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Path not found in internal API")

    return response
