from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import random, ipaddress

@router.get("/net/random-ip", tags=["network"])
async def net_random_ip(count: int = Query(default=5, ge=1, le=100)):
    ips = []
    for _ in range(count):
        ips.append(str(ipaddress.IPv4Address(random.randint(0x01000000, 0xfeffffff))))
    return {"code": "200", "count": count, "ips": ips}
