from typing import Any

from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator

from schemas.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    QueryBase,
    Status,
    Name,
)
from schemas.person import PersonList
from core.config import settings


class Address(BaseModel):
    city: str | None
    country: str | None
    country_code: str | None
    lat: float | str | None
    lng: float | str | None
    postcode: str | None = None
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
    date: int | Any = None
    from_date: int | Any = None
    order: int | Any = None
    rank: str | None = None
    source: str | None = None
    to_date: str | Any = None


class Relation(BaseModel):
    id: str | None = None
    name: str | None | Name
    types: list[Type] | None = None


class AffiliationBase(BaseModel):
    id: str | None | Any
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


class AffiliationRelated(AffiliationBase):
    name: str | None = None

    @model_validator(mode="after")
    def get_name(self) -> Self:
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)
        self.name = es_name.name if es_name else self.names[0].name
        if not isinstance(self.id, str):
            self.id = str(self.id)
        return self


class AffiliationSearch(AffiliationBase):
    id: str | None = None
    name: str | None = None
    logo: str | None = ""

    @model_validator(mode="after")
    def get_name_and_logo(self) -> Self:
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)
        self.name = es_name.name if es_name else self.names[0].name
        self.names = None
        for ext in self.external_urls:
            if ext.source == "logo":
                self.logo = ext.url
                self.external_urls.remove(ext)
        return self

    products_count: int | None = None
    citations_count: int | None = None
    affiliations: list[dict[str, Any]] | None = None


class AffiliationReduced(BaseModel):
    id: str
    name: str | None = None


class AffiliationRelatedInfo(BaseModel):
    faculties: list[AffiliationReduced] | None = None
    departments: list[AffiliationReduced] | None = None
    groups: list[AffiliationReduced] | None = None
    authors: list[PersonList] | None = None


class AffiliationQueryParams(QueryBase):
    type: str | None = None

    @property
    def get_search(self) -> dict[str, Any]:
        return {
            "types.type": (
                {"$in": settings.institutions}
                if self.type.lower() == "institution"
                else self.type
            )
        }
