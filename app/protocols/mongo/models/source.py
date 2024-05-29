from typing import Any, Protocol, NewType

from protocols.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
)

ObjectId = NewType("ObjectId", str)


class Publisher(Protocol):
    id: ObjectId | str | None
    name: str | Any | None
    country_code: str | Any | None


class Waiver(Protocol):
    has_waiver: bool | Any | None
    url: str | Any | None


class APC(Protocol):
    charges: int | Any | None
    currency: str | Any | None
    year_published: str | int | None 


class Copyright(Protocol):
    author_retains: bool | Any | None
    url: str | Any | None


class Licence(Protocol):
    BY: bool | Any | None
    NC: bool | Any | None
    ND: bool | Any | None
    SA: bool | Any | None
    type: str | Any | None
    url: str | Any | None


class SubjectEmbedded(Protocol):
    id: ObjectId | str | None
    level: int | None
    name: str | None


class Subject(Protocol):
    source: str | None
    subjects: list[SubjectEmbedded]


class Ranking(Protocol):
    from_date: float | int
    issn: Any | None
    order: int | None
    rank: str | int | float | None
    source: str | None
    to_date: float | int


class Source(Protocol):
    updated: list[Updated] | None
    names: list[Name]
    abbreviations: list[str] | None
    types: list[Type] | None
    keywords: list[str] | None
    languages: list[str] | None
    publisher: Publisher | str | None
    relations: list[Any] | None
    addresses: list[Any] | None
    external_ids: list[ExternalId] | None
    external_urls: list[ExternalURL] | None
    review_process: Any
    review_processes: list[Any] | None
    waiver: Waiver | Any | None
    plagiarism_detection: bool
    open_access_start_year: int | Any | None
    publication_time_weeks: int | Any | None
    apc: APC | None
    copyright: Copyright | Any | None
    licenses: list[Licence] | None
    subjects: list[Subject] | None
    ranking: list[Ranking] | None
    date_published: str | int | None 
