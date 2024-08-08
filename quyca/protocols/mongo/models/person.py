from typing import Any, Protocol, NewType

from quyca.protocols.mongo.models.general import Type, Updated, ExternalId


ObjectId = NewType("ObjectId", str)


class Affiliation(Protocol):
    id: ObjectId | str | None
    name: str | None
    types: list[Type] | None
    start_date: int | str | None
    end_date: int | str | None
    position: str | None


class Ranking(Protocol):
    date: str | int | None
    rank: str | None
    source: str | None
    id: str | Any | None
    order: int | Any | None


class BirthPlace(Protocol):
    city: str | None
    state: str | None
    country: str | None


class Degree(Protocol):
    date: str | int | None
    degree: str | None
    id: str | None
    institutions: list[str] | None
    source: str | None


class Person(Protocol):
    updated: list[Updated]
    full_name: str | None
    first_names: list[str]
    last_names: list[str]
    initials: str | list[str] | None
    aliases: list[str]
    affiliations: list[Affiliation]
    keywords: list[str]
    external_ids: list[ExternalId]
    sex: str | None
    marital_status: str | None
    ranking: list[Ranking]
    birthplace: BirthPlace
    birthdate: int | str
    degrees: list[Degree]
    subjects: list[Any]
