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

class Publisher(BaseModel):
    id: ObjectId | str | None = None
    name: str | Any | None = None
    country_code: str | Any | None = None


class Waiver(BaseModel):
    has_waiver: bool | Any | None = None
    url: str | Any | None = None


class APC(BaseModel):
    charges: int | Any | None = None
    currency: str | Any | None = None


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
    id: ObjectId | str | None = None
    level: int | None = None
    name: str | None = None


class Subject(BaseModel):
    source: str | None
    subjects: list[SubjectEmbedded]


class Ranking(BaseModel):
    from_date: float | int | None = None
    issn: Any | None = None
    order: int | None = None
    rank: str | int | float | None = None
    source: str | None = None


class Source(Model):
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
    review_process: Any = None
    review_processes: list[Any] | None = Field(default_factory=list)
    waiver: Waiver | Any | None = None
    plagiarism_detection: bool = Field(default_factory=list)
    open_access_start_year: int | Any | None = None
    publication_time_weeks: int | Any | None = None
    apc: APC | Any | None
    copyright: Copyright | Any | None = None
    licenses: list[Licence] | None = Field(default_factory=list)
    subjects: list[Subject] | None = Field(default_factory=list)
    ranking: list[Ranking] | None = Field(default_factory=list)

    model_config = {"collection": "sources"}