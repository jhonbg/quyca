from bson import ObjectId
from pydantic import BaseModel, Field

from database.models.base_model import (
    Type,
    Updated,
    ExternalId,
    ExternalUrl,
    Name,
    PyObjectId,
    Ranking,
    Subject,
    Publisher,
    APC,
)


class Copyright(BaseModel):
    author_retains: bool | None = None
    url: str | None = None


class Licence(BaseModel):
    BY: bool | None
    NC: bool | None
    ND: bool | None
    SA: bool | None
    type: str | None
    url: str | None = None


class Waiver(BaseModel):
    has_waiver: bool | None = None
    url: str | None = None


class Source(BaseModel):
    id: PyObjectId = Field(alias="_id")
    abbreviations: list[str] | None = None
    addresses: list | None = None
    apc: APC | None = None
    copyright: Copyright | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    keywords: list[str] | None = None
    languages: list[str] | None = None
    licenses: list[Licence] | None = None
    names: list[Name] | None = None
    open_access_start_year: int | None = None
    plagiarism_detection: bool | None = None
    publication_time_weeks: int | None = None
    publisher: Publisher | str | None = None
    ranking: list[Ranking] | None = None
    relations: list | None = None
    review_process: list[str] | None = None
    review_processes: list | None = None
    subjects: list[Subject] | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None
    waiver: Waiver | None = None

    date_published: str | int | None = None
    affiliation_names: list[Name] | None = None

    class Config:
        json_encoders = {ObjectId: str}
