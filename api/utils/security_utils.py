"""
Utilitaires de sécurité
"""

from fastapi import Request
from typing import Optional

def get_api_key(request: Request) -> Optional[str]:
    """
    Extrait la clé API depuis les headers ou les paramètres de requête
    """
    pass

def verify_api_access(api_key: str) -> bool:
    """
    Vérifie si la clé API est valide
    """
    pass