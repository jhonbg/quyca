from typing import Any

from odmantic import Model, Field
from pydantic import BaseModel

from infraestructure.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
    Status
)


class Address(BaseModel):
    city: str
    country: str
    country_code: str
    lat: float | str | None
    lng: float | str | None
    postcode: str
    state: str | None


class DescriptionEmbedded(BaseModel):
    TXT_ESTADO_ARTE: str
    TXT_OBJETIVOS: str
    TXT_PLAN_TRABAJO: str
    TXT_PROD_DESTACADA: str
    TXT_RETOS: str
    TXT_VISION: str


class Description(BaseModel):
    description: DescriptionEmbedded
    source: str


class Ranking(BaseModel):
    date: int | Any
    from_date: int | Any
    order: int | Any
    rank: str | None
    source: str | None
    to_date: str | Any

class Relation(BaseModel):
    id: Any
    name: str | None
    type: Type | None


class Affiliation(Model):
    abbreviations: list[str] | None = Field(default_factory=list)
    addresses: list[Address] | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: int | Any
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    names: list[Name] | None = Field(default_factory=list)
    ranking: Ranking | None
    relations: list[Relation] | None = Field(default_factory=list)
    status: Status | None
    subjects: list[Any] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    year_established: int

    class Config:
        collection = "affiliations"


