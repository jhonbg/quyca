from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field

from database.models.base_model import PyObjectId, CitationsCount, Type, ExternalId, ExternalURL, Subject, Updated, Ranking


class Affiliation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: str | None
    types: list[Type] | None = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}


class Author(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    affiliations: list[Affiliation] | None = Field(default_factory=list)
    full_name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class BiblioGraphicInfo(BaseModel):
    bibtex: str | None = None
    is_open_access: bool | None = None
    issue: str | None = None
    open_access_status: str | None = None
    pages: str | None = None
    start_page: str | None = None
    end_page: str | None = None
    volume: str | int | None = None


class CitationByYear(BaseModel):
    cited_by_count: int | None
    year: int | None


class Group(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Source(BaseModel):
    id: PyObjectId | str | None = Field(default_factory=PyObjectId)
    name: str | Any | None = None

    class Config:
        json_encoders = {ObjectId: str}


class Title(BaseModel):
    lang: str | None
    provenance: str | None = None
    source: str | None
    title: str | None


class ProductType(BaseModel):
    name: str | None = None
    source: str | None = None


class Work(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    abstract: str | None = None
    author_count: int | None = None
    authors: list[Author] | None = Field(default_factory=list)
    bibliographic_info: BiblioGraphicInfo | None = Field(default_factory=BiblioGraphicInfo)
    citations: list | None = Field(default_factory=list)
    citations_by_year: list[CitationByYear] | None = Field(default_factory=list)
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    date_published: int | None = None
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    groups: list[Group] | None = Field(default_factory=list)
    keywords: list | None = Field(default_factory=list)
    ranking: list[Ranking] | None = Field(default_factory=list)
    references: list | None = Field(default_factory=list)
    references_count: int | None = None
    source: Source | None = Field(default_factory=Source)
    subjects: list[Subject] | None = Field(default_factory=list)
    subtitle: str | None = None
    titles: list[Title] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    year_published: int | str | None = None

    class Config:
        json_encoders = {ObjectId: str}
