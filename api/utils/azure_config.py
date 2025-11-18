"""
Configuration simplifiée pour Azure Functions
Utilise les variables d'environnement Azure
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DataConfig:
    """Configuration du service de données"""
    base_url: str


@dataclass
class AzureConfig:
    """Configuration Azure"""
    data: DataConfig


def load_config() -> AzureConfig:
    """
    Charge la configuration depuis les variables d'environnement Azure
    
    Pour Azure Functions, utilise:
    - local.settings.json (développement local)
    - Configuration Application Settings dans Azure Portal (production)
    
    Returns:
        AzureConfig: Configuration de l'application
    """
    
    data_base_url = os.getenv(
        "DATA_SERVICE_BASE_URL",
        "http://de5.azurhosts.com:25692/"
    )
    
    return AzureConfig(
        data=DataConfig(base_url=data_base_url)
    )


# Configuration globale
config = load_config()

__all__ = ['config', 'AzureConfig', 'DataConfig']
