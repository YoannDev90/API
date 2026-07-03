"""Self-ping to prevent Render from sleeping"""

import asyncio
import logging
import os

import httpx

logger = logging.getLogger("keep-alive")

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")


async def start_self_ping():
    if not RENDER_URL:
        logger.info("RENDER_EXTERNAL_URL not set, keep-alive disabled")
        return None

    async def _ping():
        while True:
            await asyncio.sleep(600)
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(f"{RENDER_URL}/health")
                    logger.debug(f"Self-ping -> {resp.status_code}")
            except Exception as e:
                logger.warning(f"Self-ping failed: {e}")

    task = asyncio.create_task(_ping())
    logger.info(f"Keep-alive started -> {RENDER_URL}/health every 10min")
    return task
