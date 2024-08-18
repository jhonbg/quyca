from typing import Any

from pydantic import BaseModel, Field, model_validator

from models.base_model import Type, Updated, ExternalId, ExternalURL, CitationsCount, Name, PyObjectId
from models.person_model import Person


class Address(BaseModel):
    city: str | None
    country: str | None
    country_code: str | None
    lat: float | str | None
    lng: float | str | None
    postcode: str | None = None
    state: str | None


class DescriptionText(BaseModel):
    TXT_ESTADO_ARTE: str
    TXT_OBJETIVOS: str
    TXT_PLAN_TRABAJO: str
    TXT_PROD_DESTACADA: str
    TXT_RETOS: str
    TXT_VISION: str


class Description(BaseModel):
    description: DescriptionText
    source: str


class Ranking(BaseModel):
    date: int | Any = None
    from_date: int | Any = None
    order: int | Any = None
    rank: str | None = None
    source: str | None = None
    to_date: str | Any = None


class Relation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: str | None | Name
    types: list[Type] | None = None


class AffiliationBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    names: list[Name] | None = Field(default_factory=list)
    relations: list[Relation] | None = Field(default_factory=list)
    addresses: list[Address] | Address | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    types: list[Type] | Type | None = Field(default_factory=list)


class Affiliation(AffiliationBase):
    abbreviations: list[str] | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: str | int | None = None
    ranking: Ranking | list[Ranking] | None
    status: Any
    subjects: list[Any] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    year_established: int | None
    name: str | None = None

    @model_validator(mode="after")
    def get_name(self):
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)

        self.name = es_name.name if es_name else self.names[0].name

        return self



class AffiliationSearch(AffiliationBase):
    id: str | None = None
    name: str | None = None
    logo: str | None = ""

    @model_validator(mode="after")
    def get_name_and_logo(self):
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)
        self.name = es_name.name if es_name else self.names[0].name
        self.names = None
        for ext in self.external_urls:
            if ext.source == "logo":
                self.logo = ext.url
                self.external_urls.remove(ext)
        return self

    products_count: int | None = None
    citations_count: list[CitationsCount] | None = None
    affiliations: list[dict[str, Any]] | None = None


class AffiliationInfo(AffiliationSearch):
    names: list[Name] | None = Field(default_factory=list, exclude=True)
    relations: list[Relation] | None = Field(default_factory=list, exclude=True)


class AffiliationReduced(BaseModel):
    id: str
    name: str | None = None


class AffiliationRelatedInfo(BaseModel):
    faculties: list[AffiliationReduced] | None = None
    departments: list[AffiliationReduced] | None = None
    groups: list[AffiliationReduced] | None = None
    authors: list[Person] | None = None


