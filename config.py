from pydantic_settings import BaseSettings


class Config(BaseSettings):
    base_url: str = ""
    model_config = {"env_prefix": "DATA_SERVICE_", "extra": "ignore"}


config = Config()

__all__ = ["config"]
