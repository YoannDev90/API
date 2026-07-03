import os
from dataclasses import dataclass


@dataclass
class Config:
    base_url: str


config = Config(base_url=os.getenv("DATA_SERVICE_BASE_URL", ""))
allowed_proxy_paths: set[str] = set()

__all__ = ["config", "allowed_proxy_paths"]
