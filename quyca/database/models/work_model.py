from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field

from database.models.base_model import (
    PyObjectId,
    CitationsCount,
    Type,
    ExternalId,
    ExternalUrl,
    Subject,
    Updated,
    Ranking,
    Address,
    Publisher,
    APC,
)


class Affiliation(BaseModel):
    id: PyObjectId = None
    name: str | None = None
    types: list[Type] | None = None

    addresses: list[Address] | None = None
    ranking: list[Ranking] | None = None

    class Config:
        json_encoders = {ObjectId: str}


class Author(BaseModel):
    id: PyObjectId = None
    affiliations: list[Affiliation] | None = None
    full_name: str | None

    external_ids: list[ExternalId] | None = None

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
    id: PyObjectId = None
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Source(BaseModel):
    id: PyObjectId | str | None = None
    name: str | Any | None = None

    scimago_quartile: str | None = None
    serials: dict | None = None
    external_urls: list[ExternalUrl] | None = None
    ranking: list[Ranking] | None = None
    publisher: Publisher | str | None = None
    apc: APC | None = None

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
    id: PyObjectId = Field(alias="_id")
    abstract: str | None = None
    author_count: int | None = None
    authors: list[Author] | str | None = None
    bibliographic_info: BiblioGraphicInfo | None = None
    citations: list | None = Field(default_factory=list)
    citations_by_year: list[CitationByYear] | None = None
    citations_count: list[CitationsCount] | str | None = None
    date_published: int | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    groups: list[Group] | str | None = None
    keywords: list | None = None
    ranking: list[Ranking] | str | None = None
    references: list | None = None
    references_count: int | None = None
    source: Source | None = None
    subjects: list[Subject] | str | None = None
    subtitle: str | None = None
    titles: list[Title] | str | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None
    year_published: int | str | None = None

    source_data: Source | None = None
    affiliations_data: list[Affiliation] | None = None
    openalex_citations_count: str | None = None
    scholar_citations_count: str | None = None
    institutions: str | None = None
    departments: str | None = None
    faculties: str | None = None
    groups_ranking: str | None = None
    is_open_access: bool | None = None
    pages: str | None = None
    start_page: str | None = None
    end_page: str | None = None
    bibtex: str | None = None
    doi: str | None = None
    issue: str | None = None
    language: str | None = None
    open_access_status: str | None = None
    product_types: list[ProductType] | None = None
    publisher: str | None = None
    openalex_types: str | None = None
    scienti_types: str | None = None
    scimago_quartile: str | None = None
    source_apc: str | None = None
    source_name: str | None = None
    source_urls: str | None = None
    title: str | None = None
    volume: str | int | None = None

    class Config:
        json_encoders = {ObjectId: str}
