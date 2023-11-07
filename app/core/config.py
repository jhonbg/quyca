from functools import lru_cache
from typing import Any, Dict, List

from pydantic import BaseSettings

# from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application.
    """

    #: The application name
    APP_NAME: str = "Digishop cotizador database Api"
    #: The application version
    APP_VERSION: str = "0.0.1"
    #: The application debug mode
    DEBUG: bool = False
    #: The application api version
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    SECRET_KEY: str

    ALGORITHM: str = "HS256"


@lru_cache()
def get_settings() -> BaseSettings:
    """Get the settings for the application."""
    return Settings()


settings: Settings = Settings()
