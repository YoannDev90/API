from logging import getLogger

from fastapi import APIRouter, HTTPException, Query, Request


logger = getLogger("api-proxy")
router = APIRouter()




STATUS = {
    100: "Continue", 101: "Switching Protocols", 200: "OK", 201: "Created", 204: "No Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified", 307: "Temporary Redirect",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 408: "Request Timeout", 409: "Conflict", 410: "Gone",
    418: "I'm a Teapot", 422: "Unprocessable Entity", 429: "Too Many Requests",
    500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout",
}

@router.get("/http-status", tags=["utils"])
async def http_status_info(code: int = Query(..., description="HTTP status code", ge=100, le=599)):
    name = STATUS.get(code, "Unknown")
    cat = f"{code // 100}xx"
    cats = {"1xx": "Informational", "2xx": "Success", "3xx": "Redirection", "4xx": "Client Error", "5xx": "Server Error"}
    return {"code": "200", "status_code": code, "name": name, "category": cats.get(cat, "Unknown")}

