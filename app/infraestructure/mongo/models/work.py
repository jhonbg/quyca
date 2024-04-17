from typing import Any

from odmantic import Model, EmbeddedModel, Field, ObjectId
from pydantic import BaseModel

from infraestructure.mongo.models.general import (
    Type,
    Updated,
    ExternalId,
    ExternalURL,
    Name,
)


class Title(EmbeddedModel):
    title: str | None
    lang: str | None
    source: str | None


class BiblioGraphicInfo(BaseModel):
    volume: str | int | None = None
    is_open_access: bool | None = None
    open_access_status: str | None = None
    end_page: str | None = None
    issue: str | None = None
    start_page: str | None = None
    bibtex: str | None = None
    pages: str | None = None


class CitationsCount(EmbeddedModel):
    source: str | None
    count: int | None


class Affiliation(EmbeddedModel):
    id: ObjectId | str | None
    name: str | None
    types: list[Type] | None = Field(default_factory=list)


class Author(EmbeddedModel):
    id: ObjectId | str | None
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_factory=list)


class Source(BaseModel):
    id: ObjectId | str | None = None
    name: str | Any | None = None


class SubjectEmbedded(EmbeddedModel):
    id: ObjectId | str | None
    names: list[Name] | None = Field(default_factory=list)
    level: int


class Subject(EmbeddedModel):
    source: str
    subjects: list[SubjectEmbedded] | None = Field(default_factory=list)


class CitationByYear(EmbeddedModel):
    cited_by_count: int | None
    year: int | None

class CitationsCount(EmbeddedModel):
    source: str | None
    count: int | None


class SubjectEmbedded(EmbeddedModel):
    id: ObjectId | str | None = None
    level: int
    name: str


class Subject(EmbeddedModel):
    source: str | None
    subjects: list[SubjectEmbedded]

class Work(Model):
    titles: list[Title] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    subtitle: str
    abstract: str
    keywords: list[str] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    date_published: int | None
    year_published: int | None
    bibliographic_info: BiblioGraphicInfo | None
    references_count: int | None
    references: list[Any] | None = Field(default_factory=list)
    citations: list[CitationsCount] | None = Field(default_factory=list)
    author_count: int
    source: Source | None = None
    citations_by_year: list[CitationByYear] | None | Any = Field(default_factory=list)
    authors: list[Author]
    citations_count: list[CitationsCount]
    subjects: list[Subject] | None = Field(default_factory=list)

    model_config = {"collection": "works"}
