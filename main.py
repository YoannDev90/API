import logging

import uvicorn

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("api-proxy")
logger.setLevel(logging.INFO)

for noisy in ("httpx", "httpcore", "uvicorn", "fastapi"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
