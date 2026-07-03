import os
from dataclasses import dataclass


@dataclass
class DataConfig:
    base_url: str


@dataclass
class Config:
    data: DataConfig


def load_config() -> Config:
    data_base_url = os.getenv("DATA_SERVICE_BASE_URL", "")
    return Config(data=DataConfig(base_url=data_base_url))


config = load_config()
allowed_proxy_paths = set()

__all__ = ["config", "Config", "DataConfig", "allowed_proxy_paths"]
