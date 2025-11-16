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
from datetime import datetime
from typing import Optional
from colorama import Fore, Style, init
from config import config

# Initialiser colorama
init(autoreset=True)


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
        self.worker_thread.start()
        
    def _worker(self):
        """Worker thread qui envoie les logs à Grafana"""
        while not self.stop_event.is_set():
            try:
                log_entry = self.log_queue.get(timeout=5)
                if log_entry is None:  # Signal d'arrêt
                    break
                    
                self._send_to_grafana(log_entry)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️  Erreur worker Grafana: {type(e).__name__}: {e}", file=sys.stderr)
    
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
                timeout=5  # Timeout réduit
            )

            # Vérification du statut de réponse
            if response.status_code not in (200, 201, 204):
                print(f"⚠️  Erreur Grafana (HTTP {response.status_code})", file=sys.stderr)

        except requests.exceptions.Timeout:
            pass  # Silencieux - le worker ne doit pas bloquer
        except requests.exceptions.ConnectionError:
            pass  # Silencieux
        except Exception as e:
            pass  # Silencieux - ne pas bloquer le worker
        
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
            pass  # Queue pleine, ignorer ce log
        except Exception:
            pass  # Ne pas bloquer l'application
    
    def close(self):
        """Fermer proprement le handler"""
        self.stop_event.set()
        self.log_queue.put(None)  # Signal d'arrêt
        self.worker_thread.join(timeout=2)
        super().close()


def setup_logger(
    name: str,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None,
    log_level: str = "INFO",
    grafana_url: str = "https://logs-prod-012.grafana.net"
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    if logger.handlers:
        logger.handlers.clear()
    
    # Handler console avec couleurs
    console_handler = logging.StreamHandler()
    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    # Handler Grafana Cloud
    if user_id and api_key:
        try:
            grafana_handler = GrafanaLogsHandler(
                user_id=user_id,
                api_key=api_key,
                grafana_url=grafana_url
            )
            logger.addHandler(grafana_handler)
        except Exception as e:
            print(f"⚠️  Impossible de configurer le handler Grafana: {e}", file=sys.stderr)

    return logger


# Logger par défaut
logger = setup_logger(
    "alphallm-api",
    user_id=config.grafana.user_id if config.logging.grafana else None,
    api_key=config.grafana.api_key if config.logging.grafana else None,
    log_level=config.logging.level,
    grafana_url=config.grafana.url
)

__all__ = [
    'setup_logger',
    'GrafanaLogsHandler',
    'ColoredFormatter',
    'logger'
]


