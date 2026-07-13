from logging import getLogger
from fastapi import APIRouter, Query
import random

logger = getLogger("api-proxy")
router = APIRouter()

LOREM_WORDS = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split()


@router.get("/lorem", tags=["utils"])
async def lorem_ipsum(paragraphs: int = Query(default=3, ge=1, le=50),
                      words_per: int = Query(default=50, ge=5, le=500)):
    paras = []
    for _ in range(paragraphs):
        start = random.randint(0, len(LOREM_WORDS) - 1)
        para = " ".join(LOREM_WORDS[(start + i) % len(LOREM_WORDS)] for i in range(words_per))
        paras.append(para[0].upper() + para[1:] + ".")
    return {"code": "200", "paragraphs": paras}
