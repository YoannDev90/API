from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

CLOUD_IPS = {
    "AWS": ["aws", "amazonaws", "ec2"],
    "GCP": ["gcp", "googlecloud", "compute.googleapis"],
    "Azure": ["azure", "azureedge", "cloudapp.net"],
    "DigitalOcean": ["digitalocean"],
    "OVH": ["ovh"],
    "Hetzner": ["hetzner"],
    "Linode": ["linode"],
    "Vultr": ["vultr"],
}

@router.get("/net/cloud", tags=["network"])
async def net_cloud(domain: str = Query(..., description="Domain to check")):
    import dns.resolver, socket
    ips = []
    try:
        for a in dns.resolver.resolve(domain, "A"):
            ips.append(str(a))
    except: pass
    cloud = []
    for ip in ips:
        try:
            hostname = socket.gethostbyaddr(ip)[0].lower()
            for provider, keywords in CLOUD_IPS.items():
                if any(k in hostname for k in keywords):
                    cloud.append(provider)
                    break
        except: pass
    return {"code": "200", "domain": domain, "ip": ips, "cloud_providers": list(set(cloud)) or ["unknown"]}
