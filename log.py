"""
Configuration du logging pour AlphaLLM API
Envoie les logs vers Grafana Cloud via l'API Loki (asynchrone)
"""


import logging
import json
import sys
import requests
import time
import threading
import queue
import os
from datetime import datetime
from typing import Optional
from pathlib import Path
from colorama import Fore, Style, init
from config import config

# Initialiser colorama
init(autoreset=True)

# Variable globale pour stocker l'instance du handler Grafana (ne doit jamais être fermée)
_grafana_handler_instance = None


class ColoredFormatter(logging.Formatter):
    """Formatter personnalisé avec couleurs pour les logs console"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelname, Fore.WHITE)
        
        # Formater le timestamp
        asctime = self.formatTime(record, self.datefmt)
        
        # Format coloré: timestamp - logger - level - message
        formatted = (
            f"{Fore.CYAN}{asctime}{Style.RESET_ALL} - "
            f"{Fore.BLUE}{record.name}{Style.RESET_ALL} - "
            f"{level_color}{record.levelname}{Style.RESET_ALL} - "
            f"{record.getMessage()}"
        )
        return formatted


class GrafanaLogsHandler(logging.Handler):
    """
    Handler personnalisé pour envoyer les logs à Grafana Cloud via l'API Loki
    Utilise une queue asynchrone pour ne pas bloquer l'application
    """
    
    def __init__(
        self,
        user_id: str,
        api_key: str,
        grafana_url: str = "https://logs-prod-012.grafana.net"
    ):
        super().__init__()
        self.user_id = user_id
        self.api_key = api_key
        self.endpoint = f"{grafana_url}/loki/api/v1/push"
        
        # Queue pour les logs asynchrones
        self.log_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        
        # Thread worker pour envoyer les logs
        self.worker_thread = threading.Thread(
            target=self._worker, 
            daemon=True,
            name="GrafanaLogWorker"
        )
        self.worker_thread.daemon = True  # Force daemon mode
        self.worker_thread.start()
        
    def _worker(self):
        """Worker thread qui envoie les logs à Grafana"""
        while True:
            try:
                # Attendre un log (timeout court pour réactivité)
                log_entry = self.log_queue.get(timeout=0.5)
                
                if log_entry is None:  # Signal d'arrêt (ne devrait jamais arriver)
                    break
                    
                # Envoyer ce log immédiatement
                self._send_to_grafana(log_entry)
                
            except queue.Empty:
                pass
            except Exception as e:
                pass  # Ne pas bloquer le worker
    
    def _send_to_grafana(self, log_entry: dict):
        """Envoie un log à Grafana (à appeler depuis le worker thread)"""
        try:
            # Vérifie les credentials
            if not self.user_id or not self.api_key:
                return

            # Timestamp en nanosecondes pour Loki
            timestamp = log_entry.get("timestamp")
            log_text = log_entry.get("message")

            # Construction du payload pour Loki (format conforme à la spec)
            payload = {
                "streams": [
                    {
                        "stream": {
                            "job": "alphallm-api",
                            "level": log_entry.get("level", "INFO").lower(),
                            "service": "alphallm-api"
                        },
                        "values": [
                            [timestamp, log_text]
                        ]
                    }
                ]
            }

            # Envoi du log à Grafana Cloud avec Basic Auth
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.endpoint,
                auth=(self.user_id, self.api_key),
                json=payload,
                headers=headers,
                timeout=1.5
            )

            # Vérification silencieuse du statut de réponse
            if response.status_code not in (200, 201, 204):
                pass

        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass
        
    def emit(self, record: logging.LogRecord):
        """Ajoute le log à la queue (non-bloquant)"""
        try:
            # Format du log (sans couleurs pour Grafana)
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            log_entry_text = formatter.format(record)

            # Timestamp en nanosecondes pour Loki
            timestamp = str(int(time.time() * 1000000000))
            
            # Ajouter à la queue (avec timeout pour ne pas bloquer)
            log_entry = {
                "timestamp": timestamp,
                "message": log_entry_text,
                "level": record.levelname
            }
            
            self.log_queue.put(log_entry, block=False)
            
        except queue.Full:
            pass
        except Exception:
            pass
    
    def close(self):
        """Ne pas fermer le handler - le worker doit rester vivant pour toujours"""
        # Le worker est un daemon thread qui continuera à fonctionner
        # même après appel de close(). On ne fait rien ici.
        pass


def setup_logger(
    name: str,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None,
    log_level: str = "INFO",
    grafana_url: str = "https://logs-prod-012.grafana.net",
    file_path: str = "/var/log/alphallm.log"
) -> logging.Logger:
    global _grafana_handler_instance
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Supprimer UNIQUEMENT les anciens handlers du même type (pas Grafana!)
    # pour éviter de fermer les connexions Grafana
    handlers_to_remove = []
    for handler in logger.handlers:
        if not isinstance(handler, GrafanaLogsHandler):
            handlers_to_remove.append(handler)
    
    for handler in handlers_to_remove:
        logger.removeHandler(handler)
        handler.close()
    
    # Handler console avec couleurs
    console_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier pour Fail2ban
    try:
        # Créer le répertoire s'il n'existe pas
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️  Impossible de créer le handler fichier {file_path}: {e}", file=sys.stderr)

    # Handler Grafana Cloud (instance globale unique)
    if user_id and api_key:
        # Créer une seule instance et la réutiliser toujours
        if _grafana_handler_instance is None:
            try:
                _grafana_handler_instance = GrafanaLogsHandler(
                    user_id=user_id,
                    api_key=api_key,
                    grafana_url=grafana_url
                )
                logger.addHandler(_grafana_handler_instance)
            except Exception as e:
                print(f"⚠️  Impossible de configurer le handler Grafana: {e}", file=sys.stderr)
        else:
            # Ajouter l'instance existante si pas déjà présente
            if _grafana_handler_instance not in logger.handlers:
                logger.addHandler(_grafana_handler_instance)

    return logger


# Logger par défaut
logger = setup_logger(
    "alphallm-api",
    user_id=config.grafana.user_id if config.logging.grafana else None,
    api_key=config.grafana.api_key if config.logging.grafana else None,
    log_level=config.logging.level,
    grafana_url=config.grafana.url,
    file_path="/var/log/alphallm.log"
)

__all__ = [
    'setup_logger',
    'GrafanaLogsHandler',
    'ColoredFormatter',
    'logger'
]


