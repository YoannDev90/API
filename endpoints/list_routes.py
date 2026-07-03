from fastapi import APIRouter, Request
from fastapi.routing import APIRoute

router = APIRouter()


@router.get("/routes", tags=["general"])
async def list_routes(request: Request):
    app = request.app
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append(
                {
                    "path": route.path,
                    "methods": sorted(route.methods),
                    "name": route.name,
                }
            )
    return {"code": "200", "routes": routes}
