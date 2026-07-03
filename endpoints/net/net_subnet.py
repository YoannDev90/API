from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import ipaddress

@router.get("/net/subnet", tags=["network"])
async def net_subnet(cidr: str = Query(..., description="CIDR (e.g. 10.0.0.0/24)")):
    try:
        n = ipaddress.ip_network(cidr, strict=False)
        hosts = list(n.hosts())
        return {"code": "200", "network": str(n.network_address), "netmask": str(n.netmask), "wildcard": str(n.hostmask),
                "broadcast": str(n.broadcast_address), "prefixlen": n.prefixlen,
                "num_addresses": n.num_addresses, "num_hosts": max(0, n.num_addresses - 2),
                "first_host": str(hosts[0]) if hosts else None, "last_host": str(hosts[-1]) if hosts else None,
                "is_private": n.is_private}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
