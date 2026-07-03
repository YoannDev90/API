from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/user-agents/random", tags=["web"])
async def user_agents_random():
    import os, json, random
    path = os.path.join(os.path.dirname(__file__), "..", "user_agents.json")
    try:
        with open(path) as f:
            uas = json.load(f)
        name = random.choice(list(uas.keys()))
        return {"code": "200", "name": name, "user_agent": uas[name]}
    except Exception:
        return {"code": "200", "user_agent": "API-Proxy/1.0"}
