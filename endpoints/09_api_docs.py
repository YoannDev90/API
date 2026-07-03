from fastapi import APIRouter, Request
from proxy import proxy_request

router = APIRouter()


@router.get("/api/docs", tags=["internal-proxy"])
async def api_docs_proxy(request: Request):
    return await proxy_request(request, "docs")
