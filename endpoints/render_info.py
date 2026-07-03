import os
from logging import getLogger

from fastapi import APIRouter

router = APIRouter()
logger = getLogger("api-proxy")

RENDER_ENV_KEYS = [
    "RENDER_SERVICE_ID", "RENDER_SERVICE_NAME", "RENDER_SERVICE_SLUG",
    "RENDER_EXTERNAL_URL", "RENDER_EXTERNAL_HOSTNAME",
    "RENDER_INTERNAL_HOSTNAME", "RENDER_INSTANCE_ID",
    "RENDER_GIT_BRANCH", "RENDER_GIT_COMMIT", "RENDER_GIT_REPO_SLUG",
    "RENDER_CPU_COUNT", "RENDER_ENV", "RENDER_ENV_IS_DOCKER",
    "RENDER_WEB_CONCURRENCY", "RENDER_PRE_RUN_COMMAND",
]


@router.get("/render", tags=["utils"])
async def render_info():
    env = {k: os.getenv(k) for k in RENDER_ENV_KEYS if os.getenv(k)}
    env["service_url"] = "https://alphallm-api.onrender.com"
    return {
        "code": "200",
        "service": "API Proxy",
        "render": env,
    }
