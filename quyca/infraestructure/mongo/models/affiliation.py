from typing import Any

from bson import ObjectId
from odmantic import Model, Field, EmbeddedModel
from odmantic.bson import BaseBSONModel

from infraestructure.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
    CitationsCount,
)


class Address(BaseBSONModel):
    city: str | None
    country: str | None
    country_code: str | None
    lat: float | str | None
    lng: float | str | None
    postcode: str | None = None
    state: str | None


class DescriptionEmbedded(BaseBSONModel):
    TXT_ESTADO_ARTE: str
    TXT_OBJETIVOS: str
    TXT_PLAN_TRABAJO: str
    TXT_PROD_DESTACADA: str
    TXT_RETOS: str
    TXT_VISION: str


class Description(BaseBSONModel):
    description: DescriptionEmbedded
    source: str


class Ranking(BaseBSONModel):
    date: int | Any = None
    from_date: int | Any = None
    order: int | str | Any = None
    rank: str | None = None
    source: str | None = None
    to_date: str | Any = None


class Relation(EmbeddedModel):
    id: ObjectId | None | str = None
    name: str | None | Name
    types: list[Type] | None = None


class Affiliation(Model):
    abbreviations: list[str] | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: str | int | None = None
    ranking: list[Ranking] | None = None
    status: Any  # Status | list[Status] | None | str = None
    subjects: list[Any] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    year_established: int | None = None
    names: list[Name] | None = Field(default_factory=list)
    relations: list[Relation] | None = Field(default_factory=list)
    addresses: list[Address] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)

    model_config = {"collection": "affiliations"}


class Node(BaseBSONModel):
    degree: int
    id: str
    label: str
    size: float


class Edge(BaseBSONModel):
    coauthorships: int
    size: int | float
    source: str
    target: str


class CoauthorshipNetwork(BaseBSONModel):
    nodes: list[Node] | None = Field(default_factory=list)
    edges: list[Edge] | None = Field(default_factory=list)


class TopWord(BaseBSONModel):
    name: str
    value: int


class AffiliationCalculations(Model):
    coauthorship_network: CoauthorshipNetwork | None = None
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    top_words: list[TopWord]

    model_config = {"collection": "affiliations"}
