from typing import Any

from pydantic import BaseModel, Field, model_validator

from schemas.general import Type, Updated, ExternalId, ExternalURL, QueryBase, Name


class SourceQueryParams(QueryBase):
    ...


class Publisher(BaseModel):
    id: str | None
    name: str | Any | None = None
    country_code: str | Any | None = None


class Waiver(BaseModel):
    has_waiver: bool | Any | None = None
    url: str | Any | None = None


class APC(BaseModel):
    charges: int | Any | None = None
    currency: str | Any | None = None
    year_published: int | str | None = None


class Copyright(BaseModel):
    author_retains: bool | Any | None = None
    url: str | Any | None = None


class Licence(BaseModel):
    BY: bool | Any | None = None
    NC: bool | Any | None = None
    ND: bool | Any | None = None
    SA: bool | Any | None = None
    type: str | Any | None = None
    url: str | Any | None = None


class SubjectEmbedded(BaseModel):
    id: str | None = None
    level: int | None = None
    name: str | None = None


class Subject(BaseModel):
    source: str | None
    subjects: list[SubjectEmbedded]


class Ranking(BaseModel):
    from_date: float | int
    issn: Any | None = None
    order: int | None = None
    rank: str | int | float | None = None
    source: str | None = None
    to_date: float | int


class Source(BaseModel):
    updated: list[Updated] | None = Field(default_factory=list)
    names: list[Name]
    abbreviations: list[str] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    keywords: list[str] | None = Field(default_factory=list)
    languages: list[str] | None = Field(default_factory=list)
    publisher: Publisher | str | None = None
    relations: list[Any] | None = Field(default_factory=list)
    addresses: list[Any] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    review_process: list[str] | Any | None = Field(default_factory=list)
    review_processes: list[Any] | None = Field(default_factory=list)
    waiver: Waiver | Any | None = None
    plagiarim_detection: bool = Field(default_factory=list)
    open_access_start_year: int | Any | None = None
    publication_time_weeks: int | Any | None = None
    apc: APC | Any | None
    copyright: Copyright | Any | None = None
    licenses: list[Licence] | None = Field(default_factory=list)
    subjects: list[Subject] | None = Field(default_factory=list)
    ranking: list[Ranking] | None = Field(default_factory=list)
    date_published: str | int | None = Field(None, exclude=True)
    scimago_quartile: str | None = Field(None, exclude=True)

    @model_validator(mode="after")
    def get_scimag_quartile(self):
        if self.ranking:
            for rank in self.ranking:
                if rank.source == "scimago Best Quartile" and rank.rank != "-":
                    self.scimago_quartile = rank.rank
        return self
