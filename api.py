import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

API_ENDPOINT = "http://de5.azurhosts.com:25692"

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

@app.get("/")
async def read_root():
    """Proxy vers le endpoint racine du bot"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_ENDPOINT}/")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
async def status_check():
    """Proxy vers le endpoint /status du bot"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_ENDPOINT}/status")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Point d'entrée Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render fournit PORT en env
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info")
