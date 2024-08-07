from typing import Any, Protocol, NewType

from quyca.protocols.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
    CitationsCount
)

ObjectId = NewType('ObjectId', str)


class Address(Protocol):
    city: str | None
    country: str | None
    country_code: str | None
    lat: float | str | None
    lng: float | str | None
    postcode: str | None = None
    state: str | None


class DescriptionEmbedded(Protocol):
    TXT_ESTADO_ARTE: str
    TXT_OBJETIVOS: str
    TXT_PLAN_TRABAJO: str
    TXT_PROD_DESTACADA: str
    TXT_RETOS: str
    TXT_VISION: str


class Description(Protocol):
    description: DescriptionEmbedded
    source: str


class Ranking(Protocol):
    date: int | Any = None
    from_date: int | Any = None
    order: int | Any = None
    rank: str | None = None
    source: str | None = None
    to_date: str | Any = None

class Relation(Protocol):
    id: ObjectId | None | str = None
    name: str | None | Name
    types: list[Type] | None = None
    

class Affiliation(Protocol):
    abbreviations: list[str] | None 
    aliases: list[str] | None
    birthdate: str | int | None
    ranking: list[Ranking] | None = None
    status: Any#Status | list[Status] | None | str = None
    subjects: list[Any] | None
    updated: list[Updated] | None
    year_established: int | None
    names: list[Name] | None
    relations: list[Relation] | None
    addresses: list[Address] | None
    external_ids: list[ExternalId] | None 
    external_urls: list[ExternalURL] | None 
    types: list[Type] | None


class Node(Protocol):
    degree: int
    id: str
    label: str
    size: float


class Edge(Protocol):
    coauthorships: int
    size: int | float
    source: str
    target: str
    

class CoauthorshipNetwork(Protocol):
    nodes: list[Node] | None
    edges: list[Edge] | None


class TopWord(Protocol):
    name: str
    value: int

class AffiliationCalculations(Protocol):
    coauthorship_network: CoauthorshipNetwork | None = None
    citations_count: list[CitationsCount] | None
    top_words: list[TopWord]