import os
import httpx
import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Liste d'endpoints : par défaut deux endpoints connus, mais on peut écraser via
# la variable d'environnement API_ENDPOINTS (comma-separated).
_default_endpoints = ["http://de5.azurhosts.com:25692", "http://90.100.195.13:25692"]
_raw_endpoints = os.environ.get("API_ENDPOINTS")
if _raw_endpoints:
    API_ENDPOINTS = [e.strip().rstrip("/") for e in _raw_endpoints.split(",") if e.strip()]
else:
    API_ENDPOINTS = _default_endpoints


async def _try_endpoints(path: str):
    """Essaie chaque endpoint dans l'ordre et retourne la réponse JSON du premier qui répond.
    Lève la dernière exception si aucun endpoint ne répond correctement.
    """
    last_exc = None
    async with httpx.AsyncClient(timeout=5.0) as client:
        for ep in API_ENDPOINTS:
            url = f"{ep.rstrip('/')}{path}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                last_exc = e
                # continue to next endpoint
                continue
    raise last_exc or Exception("No endpoints configured")


# Health-check / cache pour /status :
# - Tâche en background qui ping l'endpoint primaire (API_ENDPOINTS[0]) toutes les 60s
# - Si l'endpoint primaire répond, on met en cache sa réponse pendant 30s
# - Si non, on laisse la cache expirée et /status utilisera la logique de fallback
_cached_status = {"data": None, "expires_at": 0}
_health_task = None

async def _health_check_primary():
    """Boucle infinie (startup): ping primary /status toutes les 60s.
    Si OK, met en cache la réponse pour 30s.
    """
    global _cached_status
    if not API_ENDPOINTS:
        return
    primary = API_ENDPOINTS[0]
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                url = f"{primary.rstrip('/')}/status"
                resp = await client.get(url)
                resp.raise_for_status()
                # Mettre en cache la réponse pour 30s
                try:
                    data = resp.json()
                except Exception:
                    data = {"status": "ok"}
                _cached_status["data"] = data
                _cached_status["expires_at"] = time.time() + 30
            except Exception:
                # clear cache (ou la laisser expirer) ; on met expires_at dans le passé
                _cached_status["data"] = None
                _cached_status["expires_at"] = 0
            # attendre 60s avant la prochaine vérification
            await asyncio.sleep(60)


# (Les handlers startup/shutdown sont ajoutés après la création de `app`)

app = FastAPI(
    title="AlphaLLM API Proxy",
    description="API proxy pour le projet AlphaLLM (via Render)",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Démarrer/arrêter la tâche au démarrage/shutdown de FastAPI
@app.on_event("startup")
async def _startup_health_task():
    global _health_task
    # lancer la tâche en background
    _health_task = asyncio.create_task(_health_check_primary())


@app.on_event("shutdown")
async def _shutdown_health_task():
    global _health_task
    if _health_task:
        _health_task.cancel()
        try:
            await _health_task
        except asyncio.CancelledError:
            pass

@app.get("/")
async def read_root():
    """Proxy vers le endpoint racine du bot"""
    try:
        return await _try_endpoints("/")
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
async def _get_first_online_endpoint():
    """Retourne l'URL du premier endpoint en ligne, ou None si aucun."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        for ep in API_ENDPOINTS:
            url = f"{ep.rstrip('/')}/"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return ep
            except Exception:
                continue
    return None


@app.get("/api_endpoint_url")
async def read_api_endpoint_url():
    """Retourne l'URL du premier endpoint en ligne."""
    try:
        endpoint = await _get_first_online_endpoint()
        if endpoint:
            return {"api_endpoint_url": endpoint}
        else:
            return {"status": "error", "message": "Aucun endpoint en ligne"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/status")
async def status_check():
    """Proxy vers le endpoint /status du bot"""
    try:
        # Si on a une réponse en cache (health-check primaire), et qu'elle n'est pas expirée,
        # on la renvoie directement.
        if _cached_status.get("data") and _cached_status.get("expires_at", 0) > time.time():
            return _cached_status["data"]

        # Sinon on fait le fallback normal (essaye chaque endpoint dans l'ordre)
        return await _try_endpoints("/status")
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Point d'entrée Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render fournit PORT en env
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info")
