import os
from functools import lru_cache
from typing import Optional
from typing_extensions import Self
from pydantic import model_validator, MongoDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        if os.getenv("ENVIRONMENT") == "dev":
            env_file = "../.env.dev"
        elif os.getenv("ENVIRONMENT") == "prod":
            env_file = "../.env.prod"
        else:
            env_file = "../.env.local"

    APP_NAME: str
    APP_VERSION: str
    APP_DEBUG: bool
    APP_PORT: str | int
    APP_DOMAIN: str

    APP_URL_PREFIX: str
    API_URL_PREFIX: str

    MONGO_SERVER: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str
    MONGO_DATABASE: str
    MONGO_PORT: int
    MONGO_CALCULATIONS_DATABASE: str
    MONGO_URI: Optional[MongoDsn] = None

    @model_validator(mode="after")
    def validate_mongo_uri(self) -> Self:
        self.MONGO_URI = MongoDsn.build(
            scheme="mongodb",
            host=self.MONGO_SERVER,
            username=self.MONGO_USERNAME,
            password=self.MONGO_PASSWORD,
            port=self.MONGO_PORT
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
