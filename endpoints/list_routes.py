from fastapi import APIRouter, Request
from fastapi.routing import APIRoute

router = APIRouter()


@router.get("/routes", tags=["general"])
async def list_routes(request: Request):
    routes = []
    for r in request.app.routes:
        if isinstance(r, APIRoute):
            routes.append({
                "path": r.path,
                "methods": sorted(r.methods),
                "name": r.name,
            })
        elif hasattr(r, "original_router"):
            for sr in r.original_router.routes:
                if isinstance(sr, APIRoute):
                    routes.append({
                        "path": sr.path,
                        "methods": sorted(sr.methods),
                        "name": sr.name,
                    })
    routes.sort(key=lambda x: x["path"])
    return {"code": "200", "count": len(routes), "routes": routes}
