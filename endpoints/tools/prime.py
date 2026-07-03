from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/prime", tags=["tools"])
async def primes_up_to(n: int = Query(default=100, ge=2, le=100000)):
    s = bytearray(b"\x01") * (n+1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5)+1):
        if s[i]: s[i*i:n+1:i] = b"\x00" * (((n-i*i)//i)+1)
    primes = [i for i,v in enumerate(s) if v]
    return {"code": "200", "limit": n, "count": len(primes), "primes": primes[:500]}

