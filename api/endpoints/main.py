from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from datetime import datetime
from logging import getLogger
import requests
from config import config
import os
from pathlib import Path

router = APIRouter()
logger = getLogger("alphallm-api")

@router.get("/", tags=["general"])
async def read_root(request: Request):
    """Point d'entrée principal de l'API"""
    # Récupérer l'IP réelle du client (Cloudflare ou autre proxy)
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")
    logger.info(f"Requête reçue à la racine de l'API depuis {client_ip}")
    return {
        "code": "200",
        "message": "AlphaLLM API",
        "version": "2.0.0",
        "client_ip": client_ip,
    }

@router.get("/favicon.ico", tags=["assets"], include_in_schema=False)
async def favicon():
    """Retourne le favicon d'AlphaLLM"""
    favicon_path = Path(__file__).parent.parent.parent / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon", headers={"Cache-Control": "public, max-age=86400"})
    # Fallback si le fichier n'existe pas
    return {"code": "404"}


@router.get("/status", tags=["general"])
async def status_check():
    """Point de contrôle de statut de l'API"""
    logger.info("Requête reçue pour le contrôle de statut de l'API")
    
    try:
        status_url = f"{config.data.base_url.rstrip('/')}/status"
        response = requests.get(status_url, timeout=5)
        
        if response.status_code == 200:
            return {
                "code": "200",
                "service": "AlphaLLM API",
                "data_service": response.json() if response.headers.get('content-type') == 'application/json' else response.text
            }
        else:
            logger.warning(f"Service de données retourne le status {response.status_code}")
            return {
                "code": str(response.status_code),
                "service": "AlphaLLM API",
                "data_service": "Service indisponible"
            }
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de la vérification du statut du service de données")
        return {
            "code": "503",
            "service": "AlphaLLM API",
            "data_service": "Timeout"
        }
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter au service de données")
        return {
            "code": "503",
            "service": "AlphaLLM API",
            "data_service": "Service indisponible"
        }
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut: {e}")
        return {
            "code": "500",
            "service": "AlphaLLM API",
            "data_service": "Erreur interne"
        }


@router.get("/debug", tags=["debug"], include_in_schema=False)
async def debug_headers(request: Request):
    """Affiche tous les en-têtes HTTP reçus, y compris les infos Cloudflare"""
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")
    logger.info(f"Requête de debug reçue depuis {client_ip}")
    
    # Convertir les headers en dict
    headers = dict(request.headers)
    
    # Extraire les informations Cloudflare et de géolocalisation
    cloudflare_info = {
        # Client IP - Adresse IP réelle du visiteur
        "cf_connecting_ip": headers.get("cf-connecting-ip", "N/A"),
        
        # Géolocalisation (si activé dans Cloudflare)
        "cf_ip_country": headers.get("cf-ipcountry", "N/A"),
        "cf_ip_city": headers.get("cf-ipcity", "N/A"),
        "cf_ip_continent": headers.get("cf-ipcontinent", "N/A"),
        "cf_ip_latitude": headers.get("cf-iplatitude", "N/A"),
        "cf_ip_longitude": headers.get("cf-iplongitude", "N/A"),
        "cf_ip_postal_code": headers.get("cf-ippostalcode", "N/A"),
        "cf_ip_timezone": headers.get("cf-iptimezone", "N/A"),
        
        # Informations de requête Cloudflare
        "cf_ray": headers.get("cf-ray", "N/A"),
        "cf_request_id": headers.get("cf-request-id", "N/A"),
        "cf_visitor": headers.get("cf-visitor", "N/A"),
        
        # TLS / SSL Cloudflare
        "cf_tls_version": headers.get("cf-tls-version", "N/A"),
        "cf_tls_cipher": headers.get("cf-tls-cipher", "N/A"),
        "cf_tls_client_auth": headers.get("cf-tls-client-auth", "N/A"),
        
        # Autres infos utiles
        "true_client_ip": headers.get("true-client-ip", "N/A"),
        "x_forwarded_for": headers.get("x-forwarded-for", "N/A"),
        "x_forwarded_proto": headers.get("x-forwarded-proto", "N/A"),
        "x_forwarded_host": headers.get("x-forwarded-host", "N/A"),
    }
    
    # Nettoyer les valeurs "N/A" pour plus de clarté
    cloudflare_info = {k: v for k, v in cloudflare_info.items() if v != "N/A"}
    
    return {
        "code": "200",
        "message": "Debug - En-têtes HTTP",
        "client_ip_resolved": client_ip,
        "cloudflare_info": cloudflare_info if cloudflare_info else "Aucune info Cloudflare détectée",
        "all_headers": headers
    }
