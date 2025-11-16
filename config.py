"""
Gestionnaire de configuration pour AlphaLLM API
Charge les variables depuis .env et config.toml
"""

import os
import sys
import toml
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class GrafanaConfig:
    """Configuration Grafana Cloud"""
    user_id: str
    api_key: str
    url: str


@dataclass
class ServerConfig:
    """Configuration du serveur"""
    host: str
    port: int
    reload: bool


@dataclass
class LoggingConfig:
    """Configuration du logging"""
    level: str
    console: bool
    grafana: bool


@dataclass
class DataConfig:
    """Configuration du service de données"""
    base_url: str


@dataclass
class AppConfig:
    """Configuration principale de l'application"""
    grafana: GrafanaConfig
    server: ServerConfig
    logging: LoggingConfig
    data: DataConfig


def load_config() -> AppConfig:
    """
    Charge la configuration depuis .env et config.toml
    .env contient les secrets (USER_ID, API_KEY)
    config.toml contient la configuration publique
    
    Returns:
        AppConfig: Configuration complète de l'application
    """
    # Répertoire de base de l'application
    base_dir = Path(__file__).parent
    
    # Charger le fichier .env (secrets uniquement)
    env_file = base_dir / ".env"
    if env_file.exists():
        try:
            load_dotenv(env_file, override=False)
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement de .env: {e}", file=sys.stderr)
    
    # Charger le fichier config.toml
    config_file = base_dir / "config.toml"
    config_data = {}
    if config_file.exists():
        try:
            config_data = toml.load(config_file)
        except Exception as e:
            print(f"❌ Erreur lors du chargement de config.toml: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"❌ Fichier config.toml manquant: {config_file}", file=sys.stderr)
        sys.exit(1)
    
    # Configuration Grafana (secrets du .env + config du toml)
    grafana_user_id = os.getenv("GRAFANA_USER_ID", "").strip()
    grafana_api_key = os.getenv("GRAFANA_API_KEY", "").strip()
    
    if not grafana_user_id or not grafana_api_key:
        print("⚠️  Variables Grafana manquantes (mode sans Grafana)", file=sys.stderr)
    
    grafana_config = GrafanaConfig(
        user_id=grafana_user_id,
        api_key=grafana_api_key,
        url=config_data.get("grafana", {}).get("url", "https://logs-prod-012.grafana.net")
    )
    
    # Configuration Serveur
    server_config = ServerConfig(
        host=config_data.get("server", {}).get("host", "0.0.0.0"),
        port=config_data.get("server", {}).get("port", 8000),
        reload=config_data.get("server", {}).get("reload", False)
    )
    
    # Configuration Logging
    logging_config = LoggingConfig(
        level=config_data.get("logging", {}).get("level", "INFO"),
        console=config_data.get("logging", {}).get("console", True),
        grafana=config_data.get("logging", {}).get("grafana", True)
    )

    # Configuration Data
    data_config = DataConfig(
        base_url=config_data.get("data", {}).get("base_url", "http://de5.azurhosts.com:25692/")
    )
    
    return AppConfig(
        grafana=grafana_config,
        server=server_config,
        logging=logging_config,
        data=data_config
    )


# Charger la configuration au démarrage
config = load_config()

__all__ = [
    'config',
    'AppConfig',
    'GrafanaConfig',
    'ServerConfig',
    'LoggingConfig',
    'DataConfig',
    'load_config'
]

