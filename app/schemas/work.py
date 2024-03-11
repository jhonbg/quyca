from typing import Any

from pydantic import BaseModel, Field, field_validator

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
    id: str
    names: list[Name] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)


class Author(BaseModel):
    id: str
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_affiliation=list)


class Source(BaseModel):
    id: str
    names: list[Name] | None = Field(default_factory=list)


class SubjectEmbedded(BaseModel):
    id: str
    name: str | None
    level: int


class Subject(BaseModel):
    source: str
    subjects: list[SubjectEmbedded] | None = Field(default_factory=list)


class CitationByYear(BaseModel):
    cited_by_count: int | None
    year: int | None


class CitationsCount(BaseModel):
    source: str | None
    count: int | None


class WorkBase(BaseModel):
    id: str | None
    title: list[Title] | None = Field(default_factory=list, alias="titles")
    authors: list[Author] = Field(default_factory=list)
    source: Source | None = Field(default_factory=dict)
    citations_count: list[CitationsCount]
    subjects: list[Subject]


class WorkSearch(WorkBase):
    @field_validator("citations_count")
    @classmethod
    def sort_citations_count(cls, v: list[CitationsCount]):
        return list(sorted(v, key=lambda x: x.count, reverse=True))


class Work(BaseModel):
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

    citations_by_year: list[CitationByYear] | None = Field(default_factory=list)


class WorkQueryParams(QueryBase):
    start_year: int | None = None
    end_year: int | None = None
    institutions: str | None = None
    groups: str | None = None
    type: str | None = None
