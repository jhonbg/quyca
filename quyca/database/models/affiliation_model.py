from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from database.models.base_model import (
    Type,
    Updated,
    ExternalUrl,
    CitationsCount,
    Name,
    PyObjectId,
    ExternalId,
    Subject,
    Ranking,
)


class Address(BaseModel):
    city: str | None
    country: str | None
    country_code: str | None
    lat: float | str | None
    lng: float | str | None
    postcode: str | None
    state: str | None


class DescriptionText(BaseModel):
    TXT_ESTADO_ARTE: str | None
    TXT_OBJETIVOS: str | None
    TXT_PLAN_TRABAJO: str | None
    TXT_PROD_DESTACADA: str | None
    TXT_RETOS: str | None
    TXT_VISION: str | None


class Description(BaseModel):
    description: DescriptionText
    source: str


class Relation(BaseModel):
    id: PyObjectId = None
    name: str | Name | None
    types: list[Type] | None


class Status(BaseModel):
    source: str | None
    status: str | None


class Affiliation(BaseModel):
    id: PyObjectId = Field(alias="_id")
    abbreviations: list[str] | None = None
    addresses: list[Address] | Address | None = None
    aliases: list[str] | None = None
    birthdate: str | int | None = None
    description: list[Description] | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    names: list[Name] | None = None
    ranking: list[Ranking] | None = None
    relations: list[Relation] | Relation | None = None
    status: list[str] | list[Status] | None = None
    subjects: list[Subject] | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None
    year_established: int | None

    name: str | None = None
    citations_count: list[CitationsCount] | None = None
    products_count: int | None = None
    logo: str | None = None
    affiliations: list | None = None

    @model_validator(mode="after")
    def get_name(self):
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)

        self.name = es_name.name if es_name else self.names[0].name

        return self

    class Config:
        json_encoders = {ObjectId: str}
