"""
Point d'entrée pour le serveur AlphaLLM API
Démarre l'application FastAPI avec Uvicorn
"""

import uvicorn
import logging
import sys
from colorama import Fore, Style, init
from api.api import app
from config import config
from log import logger, ColoredFormatter

init(autoreset=True)


class UvicornColoredFormatter(logging.Formatter):
    """Formatter pour les logs Uvicorn avec couleurs"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelname, Fore.WHITE)
        asctime = self.formatTime(record, self.datefmt)
        
        formatted = (
            f"{Fore.CYAN}{asctime}{Style.RESET_ALL} - "
            f"{Fore.BLUE}{record.name}{Style.RESET_ALL} - "
            f"{level_color}{record.levelname}{Style.RESET_ALL} - "
            f"{record.getMessage()}"
        )
        return formatted


def main():
    """Lance le serveur API"""
    logger.info(f"Démarrage du serveur AlphaLLM API sur {config.server.host}:{config.server.port}")
    
    # Configuration d'Uvicorn avec log_config pour Pylance
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
    
    uvicorn_config = uvicorn.Config(
        app,
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        log_config=log_config
    )
    
    # Remplacer les formatters des handlers Uvicorn par des formatters colorés
    server = uvicorn.Server(uvicorn_config)
    for handler in logging.root.handlers + logging.getLogger("uvicorn").handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setFormatter(UvicornColoredFormatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
    
    server.run()

if __name__ == "__main__":
    main()

