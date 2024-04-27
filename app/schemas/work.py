from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.general import Type, Updated, ExternalId, ExternalURL, QueryBase
from core.config import settings


class Title(BaseModel):
    title: str | None = None
    lang: str | None = None
    source: str | None = None


class ProductType(BaseModel):
    name: str | None = None
    source: str | None = None


class BiblioGraphicInfo(BaseModel):
    bibtex: str | Any | None
    end_page: str | Any | None
    volume: str | int | None
    issue: str | Any | None
    open_access_status: str | Any | None
    pages: str | Any | None
    start_page: str | Any | None
    is_open_access: bool | Any | None
    open_access_status: str | None


class CitationsCount(BaseModel):
    source: str
    count: int


class Name(BaseModel):
    name: str
    lang: str


class Affiliation(BaseModel):
    id: str | None = None
    name: str | None = None
    types: list[Type] | None = Field(default_factory=list)


class Author(BaseModel):
    id: str
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_affiliation=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    sex: str | None = None


class Source(BaseModel):
    id: str | None = None
    name: str | Any | None = None
    serials: Any | None = None


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
    title: str | None = None
    authors: list[Author] = Field(default_factory=list)

    @field_validator("authors")
    @classmethod
    def unic_authors_by_id(cls, v: list[Author]):
        seen = set()
        unique_authors = []
        for author in v:
            if author.id not in seen:
                seen.add(author.id)
                unique_authors.append(author)
        return unique_authors

    source: Source | None = Field(default_factory=dict)
    citations_count: list[CitationsCount] | int = Field(default_factory=list)
    subjects: list[Subject] | list[dict[str, str]]


class WorkSearch(WorkBase):
    product_type: list[ProductType] | None = Field(default_factory=list)
    types: list[Type] = Field(default_factory=list, exclude=True)

    @model_validator(mode="after")
    def get_types(self):
        self.product_type = list(
            map(lambda x: ProductType(name=x.type, source=x.source), self.types)
        )
        return self

    @field_validator("citations_count")
    @classmethod
    def sort_citations_count(cls, v: list[CitationsCount]):
        return list(sorted(v, key=lambda x: x.count, reverse=True))


class WorkListApp(WorkSearch):
    titles: list[Title] = Field(default_factory=list, exclude=True)
    year_published: int | None = None
    open_access_status: str | None = ""

    bibliographic_info: BiblioGraphicInfo = Field(exclude=True)

    @model_validator(mode="after")
    def get_title(self):
        self.title = next(
            filter(lambda x: x.lang == "en", self.titles), self.titles[0]
        ).title
        return self

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status or ""
        self.bibliographic_info = None
        return self

    external_ids: list[ExternalId] | list[dict] | None = Field(default_factory=list)


class WorkProccessed(WorkListApp):
    abstract: str | None = ""

    language: str | None = ""
    volume: str | int | None = None
    issue: str | None = None

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status
        self.volume = self.bibliographic_info.volume
        self.issue = self.bibliographic_info.issue
        self.bibliographic_info = None
        return self

    # @field_validator("subjects")
    # @classmethod
    # def get_openalex_source(cls, v: list[Subject]):
    #     open_alex_subjects = list(filter(lambda x: x.source == "openalex", v))
    #     maped_embedded_subjects = list(map(lambda x: x.subjects, open_alex_subjects))
    #     return (
    #         list(map(lambda x: {"name": x.name, "id": x.id}, *maped_embedded_subjects))
    #         if maped_embedded_subjects
    #         else []
    #     )

    external_urls: list[ExternalURL] | None = Field(default_factory=list)

    # Machete
    @model_validator(mode="before")
    @classmethod
    def get_openalex_url(cls, data: dict[str, Any]):
        openalex = next(
            filter(lambda x: x["source"] == "openalex", data["external_ids"]), None
        )
        if openalex:
            data["external_urls"] += [
                ExternalURL(url=openalex["id"], source="openalex")
            ]
        return data

    @field_validator("external_ids")
    @classmethod
    def append_urls_external_ids(cls, v: list[ExternalId]):
        scienti = list(filter(lambda x: x.provenance == "scienti", v))
        v += (
            [ExternalId(id=f"{scienti[0].id}-{scienti[1].id}", source="scienti")]
            if len(scienti) == 2
            else []
        )

        return list(
            map(
                lambda x: (
                    {
                        "id": x.id,
                        "source": x.source,
                        "url": settings.EXTERNAL_IDS_MAP.get(x.source, "").format(
                            id=x.id
                        ),
                    }
                ),
                filter(lambda x: x.source in settings.EXTERNAL_IDS_MAP, v),
            )
        )

    @field_validator("citations_count")
    @classmethod
    def get_citations_count(cls, v: list[CitationsCount]):
        return v[0].count if v else 0


class WorkCsv(WorkProccessed):
    date_published: int | float | str | None = None
    start_page: str | None = None
    end_page: str | None = None

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status
        self.volume = self.bibliographic_info.volume
        self.issue = self.bibliographic_info.issue
        self.start_page = self.bibliographic_info.start_page
        self.end_page = self.bibliographic_info.end_page
        self.bibliographic_info = None
        return self


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
