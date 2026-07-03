from pydantic_settings import BaseSettings


class Config(BaseSettings):
    base_url: str = ""
    model_config = {"env_prefix": "DATA_SERVICE_", "extra": "ignore"}


config = Config()
allowed_proxy_paths: set[str] = set()

__all__ = ["config", "allowed_proxy_paths"]
