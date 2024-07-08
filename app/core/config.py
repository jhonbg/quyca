from functools import lru_cache
from typing import Any, Optional

from typing_extensions import Self

from pydantic import model_validator, MongoDsn

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

    APP_PORT: str | int = 8010

    APP_DOMAIN: str = "localhost:8010"

    ENVIRONMENT: str = "dev"

    @model_validator(mode="after")
    def validate_mongo_uri(self) -> Self:
        self.MONGO_URI = MongoDsn.build(
            scheme="mongodb",
            host=self.MONGO_SERVER,
            username=self.MONGO_INITDB_ROOT_USERNAME,
            password=self.MONGO_INITDB_ROOT_PASSWORD,
            port=self.MONGO_INITDB_PORT
        )
        return self

    EXTERNAL_IDS_MAP: dict[str, str] = {
        "scholar": "https://scholar.google.com/scholar?hl="
        "en&as_sdt=0%2C5&q=info%3A{id}%3Ascholar.google.com",
        "doi": "https://doi.org/{id}",
        "lens": "https://www.lens.org/lens/scholar/article/{id}",
        "minciencias": "",
        "scienti": "",
    }

    TYPES: dict[str, str] = {
        "peer-review": "Revisión por partes",
        "techreport": "Informe técnico",
        "masterthesis": "Tesis de maestría",
        "dataset": "Conjunto de datos",
        "editorial": "Editorial",
        "Publicado en revista especializada": "Publicado en revista especializada",
        "report": "Informe",
        "Artículos": "Artículos",
        "letter": "Carta",
        "Corto (resumen)": "Resumen",
        "reference-entry": "Entrada de referencia",
        "dissertation": "Disertación",
        "standard": "Estándar",
        "Artículos de investigación": "Artículos de investigación",
        "Artículo": "Artículo",
        "incollection": "En colección",
        "book": "Libro",
        "article": "Artículo",
        "Caso clínico": "Caso clínico",
        "paratext": "Paratexto",
        "misc": "Misceláneo",
        "erratum": "Errata",
        "Revisión (Survey)": "Revisión",
        "inproceedings": "En actas",
    }

    institutions: list[str] = [
        "Archive",
        "Company",
        "Education",
        "Facility",
        "Government",
        "Healthcare",
        "Nonprofit",
        "Other",
        "archive",
        "company",
        "education",
        "facility",
        "government",
        "healthcare",
        "nonprofit",
        "other",
        "institution"
    ]


@lru_cache()
def get_settings() -> BaseSettings:
    """Get the settings for the application."""
    return Settings()


settings: Settings = Settings()
