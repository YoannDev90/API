from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/ip", tags=["general"])
async def client_ip(request: Request):
    client_ip = request.scope.get(
        "client_ip", request.client.host if request.client else "unknown"
    )
    forwarded = request.headers.get("X-Forwarded-For", "")
    cf_ip = request.headers.get("CF-Connecting-IP", "")
    real_ip = request.headers.get("X-Real-IP", "")
    return {
        "code": "200",
        "client_ip": client_ip,
        "x_forwarded_for": forwarded or None,
        "cf_connecting_ip": cf_ip or None,
        "x_real_ip": real_ip or None,
    }
