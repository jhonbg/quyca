from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import validator, MongoDsn

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application.
    """

    #: The application name
    APP_NAME: str = "impactu Api"
    #: The application version
    APP_VERSION: str = "0.0.1"
    #: The application debug mode
    DEBUG: bool = False
    #: The application api version
    APP_V1_STR: str = "/app/v1"
    APP_V2_STR: str = "/app/v2"
    API_V1_STR: str = "/api/v1"
    API_v2_STR: str = "/api/v2"

    MONGO_SERVER: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str
    MONGO_INITDB_PORT: int = 27017
    MONGO_IMPACTU_DB: str

    MONGO_URI: Optional[MongoDsn] = None

    @validator("MONGO_URI", pre=True)
    def validate_mongo_uri(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        return MongoDsn.build(
            scheme="mongodb",
            host=values.get("MONGO_SERVER"),
            username=values.get("MONGO_INITDB_ROOT_USERNAME"),
            password=values.get("MONGO_INITDB_ROOT_PASSWORD"),
            port=values.get("MONGO_INITDB_PORT"),
        )

    EXTERNAL_IDS_MAP: dict[str, str] = {
        "scholar": "https://scholar.google.com/scholar?hl="
        "en&as_sdt=0%2C5&q=info%3A{id}%3Ascholar.google.com",
        "doi": "https://doi.org/{id}",
        "lens": "https://www.lens.org/lens/scholar/article/{id}",
        "minciencias": "",
        "scienti": ""
    }


@lru_cache()
def get_settings() -> BaseSettings:
    """Get the settings for the application."""
    return Settings()


settings: Settings = Settings()
