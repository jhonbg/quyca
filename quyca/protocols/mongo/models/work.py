from typing import Protocol, Any, NewType

from protocols.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
)

ObjectId = NewType("ObjectId", str)


class Title(Protocol):
    title: str | None
    lang: str | None
    source: str | None


class BiblioGraphicInfo(Protocol):
    volume: str | int | None = None
    is_open_access: bool | None = None
    open_access_status: str | None = None
    end_page: str | None = None
    issue: str | None = None
    start_page: str | None = None
    bibtex: str | None = None
    pages: str | None = None


class CitationsCount(Protocol):
    source: str | None
    count: int | None


class Affiliation(Protocol):
    id: ObjectId | str | None
    name: str | None
    types: list[Type] | None


class Author(Protocol):
    id: ObjectId | str | None
    full_name: str
    affiliations: list[Affiliation] | None


class Source(Protocol):
    id: ObjectId | str | None = None
    name: str | Any | None = None


class SubjectEmbedded(Protocol):
    id: ObjectId | str | None
    names: list[Name] | None
    level: int


class Subject(Protocol):
    source: str
    subjects: list[SubjectEmbedded] | None


class CitationByYear(Protocol):
    cited_by_count: int | None
    year: int | None


class CitationsCount(Protocol):
    source: str | None
    count: int | None


class SubjectEmbedded(Protocol):
    id: ObjectId | str | None = None
    level: int
    name: str


class Subject(Protocol):
    source: str | None
    subjects: list[SubjectEmbedded]


class Ranking(Protocol):
    date: str | int
    provenance: str
    rank: str | None
    source: str


class Work(Protocol):
    titles: list[Title] | None
    updated: list[Updated] | None
    subtitle: str
    abstract: str
    keywords: list[str] | None
    types: list[Type] | None
    external_ids: list[ExternalId] | None
    external_urls: list[ExternalURL] | None
    date_published: int | None = None
    year_published: int | str | None = None
    bibliographic_info: BiblioGraphicInfo | None
    references_count: int | None = None
    references: list[Any] | None
    citations: list[CitationsCount] | None
    author_count: int | None = None
    source: Source | None = None
    citations_by_year: list[CitationByYear] | None | Any
    authors: list[Author]
    ranking: list[Ranking]
    citations_count: list[CitationsCount]
    subjects: list[Subject] | None
