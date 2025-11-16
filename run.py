#!/usr/bin/env python3

"""
Wrapper pour démarrer AlphaLLM API correctement avec systemd
Lance Uvicorn et attend les signaux d'arrêt
"""

import sys
import signal
import logging
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from api.api import app
from config import config
from log import logger

# Variables globales
server = None
should_exit = False


def signal_handler(signum, frame):
    """Gestionnaire de signaux pour arrêt gracieux"""
    global should_exit
    should_exit = True
    logger.info(f"Signal {signum} reçu, arrêt du serveur...")
    if server:
        server.should_exit = True


def main():
    """Lance le serveur API"""
    global server
    
    try:
        # Configuration des signaux
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info(f"🚀 Démarrage d'AlphaLLM API sur {config.server.host}:{config.server.port}")
        
        # Configuration Uvicorn
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "logging.Formatter",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
        }
        
        # Créer et configurer le serveur
        server = uvicorn.Server(uvicorn.Config(
            app,
            host=config.server.host,
            port=config.server.port,
            reload=False,
            log_config=log_config,
            timeout_graceful_shutdown=5,
            timeout_notify=30,
            workers=1
        ))
        
        # Lancer le serveur (bloquant)
        logger.info("✅ Serveur démarré avec succès")
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
