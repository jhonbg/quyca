from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.general import Type, Updated, ExternalId, ExternalURL, QueryBase


class Title(BaseModel):
    title: str
    lang: str
    source: str


class BiblioGraphicInfo(BaseModel):
    bibtex: str | Any
    end_page: str | Any
    volume: str | int
    issue: str | Any
    open_access_status: str | Any
    pages: str | Any
    start_page: str | Any
    is_open_access: bool | Any
    open_access_status: str


class CitationsCount(BaseModel):
    source: str
    count: int


class Name(BaseModel):
    name: str
    lang: str


class Affiliation(BaseModel):
    id: str
    name: str
    types: list[Type] | None = Field(default_factory=list)


class Author(BaseModel):
    id: str
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_affiliation=list)


class Source(BaseModel):
    id: str
    name: str | Any


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
    title: str | None = Field(default_factory=list, alias="titles")
    authors: list[Author] = Field(default_factory=list)
    source: Source | None = Field(default_factory=dict)
    citations_count: list[CitationsCount]
    subjects: list[Subject] | list[dict[str, str]]


class WorkSearch(WorkBase):
    @field_validator("citations_count")
    @classmethod
    def sort_citations_count(cls, v: list[CitationsCount]):
        return list(sorted(v, key=lambda x: x.count, reverse=True))


class WorkProccessed(WorkBase):
    titles: list[Title] = Field(default_factory=list)

    @model_validator(mode="before")
    def get_title(self):
        self.title = next(
            filter(lambda x: x.lang == "en", self.titles), self.titles[0].title
        )
        return None

    year_published: int | None = None
    open_access_status: str | None = None
    biblio_graphic_info: BiblioGraphicInfo

    @model_validator(mode="before")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.biblio_graphic_info.open_access_status

    @field_validator("subjects")
    @classmethod
    def get_openalex_source(cls, v: list[Subject]):
        open_alex_subjects = list(filter(lambda x: x.source == "openalex", v))
        maped_embedded_subjects = list(map(lambda x: x.subjects, open_alex_subjects))
        return list(
            map(lambda x: {"name": x.name, "id": x.id}, *maped_embedded_subjects)
        )


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
