from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from database.models.base_model import Type, Updated, ExternalURL, CitationsCount, Name, PyObjectId, ExternalId, \
    Subject, Ranking


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
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: str | Name | None
    types: list[Type] | None


class Status(BaseModel):
    source: str | None
    status: str | None


class Affiliation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    abbreviations: list[str] | None = Field(default_factory=list)
    addresses: list[Address] | Address | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: str | int | None = None
    description: list[Description] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    names: list[Name] | None = Field(default_factory=list)
    ranking: list[Ranking] | None = Field(default_factory=list)
    relations: list[Relation] | Relation | None = Field(default_factory=list)
    status: list[str] | list[Status] | None = Field(default_factory=list)
    subjects: list[Subject] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    year_established: int | None

    name: str | None = None
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
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
