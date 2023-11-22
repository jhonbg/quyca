from typing import Any

from odmantic import Model, EmbeddedModel, Field
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
    volume: str | int | None
    is_open_access: bool | None
    open_access_status: str | None


class CitationsCount(EmbeddedModel):
    source: str | None
    count: int | None


class Affiliation(EmbeddedModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)


class Author(EmbeddedModel):
    id: Any
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_affiliation=list)


class Source(EmbeddedModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)


class SubjectEmbedded(EmbeddedModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)
    level: int


class Subject(EmbeddedModel):
    source: str
    subjects: list[SubjectEmbedded] | None = Field(default_factory=list)


class CitationByYear(EmbeddedModel):
    cited_by_count: int | None
    year: int | None


class Work(Model):
    titles: list[Title] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    subtitle: str
    abstract: str
    keywords: list[str] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    date_published: int
    year_published: int
    bibliographic_info: BiblioGraphicInfo | None
    references_count: int | None
    references: list[Any] | None = Field(default_factory=list)
    citations: list[CitationsCount] | None = Field(default_factory=list)
    author_count: int
    source: Any  # Source | None = Field(default_factory=dict)
    citations_by_year: list[CitationByYear] | None = Field(default_factory=list)
    authors: list[Author]

    class Config:
        collection = "works"
