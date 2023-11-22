from typing import Any

from pydantic import BaseModel, Field

from schemas.general import Type, Updated, ExternalId, ExternalURL, QueryBase


class Title(BaseModel):
    title: str
    lang: str
    source: str


class BiblioGraphicInfo(BaseModel):
    volume: str | int
    is_open_access: bool
    open_access_status: str


class CitationsCount(BaseModel):
    source: str
    count: int


class Name(BaseModel):
    name: str
    lang: str


class Affiliation(BaseModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)


class Author(BaseModel):
    id: Any
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_affiliation=list)


class Source(BaseModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)


class SubjectEmbedded(BaseModel):
    id: Any
    names: list[Name] | None = Field(default_factory=list)
    level: int


class Subject(BaseModel):
    source: str
    subjects: list[SubjectEmbedded] | None = Field(default_factory=list)


class CitationByYear(BaseModel):
    cited_by_count: int | None
    year: int | None


class Work(BaseModel):
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
    bibligraphic_info: list[BiblioGraphicInfo] | None = Field(default_factory=list)
    references_count: int | None
    references: list[Any] | None = Field(default_factory=list)
    citations: list[CitationsCount] | None = Field(default_factory=list)
    author_count: int
    source: Source | None = Field(default_factory=dict)
    citations_by_year: list[CitationByYear] | None = Field(default_factory=list)
    authors: list[Author]

    class Config:
        collection = "works"


class WorkQueryParams(QueryBase):
    start_year: int | None = None
    end_year: int | None = None
    institutions: str | None = None
    groups: str | None = None
    type: str | None = None