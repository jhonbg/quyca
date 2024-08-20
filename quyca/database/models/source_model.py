from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from database.models.base_model import Type, Updated, ExternalId, ExternalURL, Name, PyObjectId, Ranking, Subject


class APC(BaseModel):
    charges: int | None = None
    currency: str | None = None
    year_published: int | None = None


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


class Publisher(BaseModel):
    id: str | None = None
    country_code: str | None = None
    name: str | float | None = None


class Waiver(BaseModel):
    has_waiver: bool | None = None
    url: str | None = None


class Source(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    abbreviations: list[str] | None = Field(default_factory=list)
    addresses: list | None = Field(default_factory=list)
    apc: APC | None = Field(default_factory=APC)
    copyright: Copyright | None = Field(default_factory=Copyright)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    keywords: list[str] | None = Field(default_factory=list)
    languages: list[str] | None = Field(default_factory=list)
    licenses: list[Licence] | None = Field(default_factory=list)
    names: list[Name] | None = Field(default_factory=list)
    open_access_start_year: int | None = None
    plagiarism_detection: bool | None = None
    publication_time_weeks: int | None = None
    publisher: Publisher | str | None = Field(default_factory=Publisher)
    ranking: list[Ranking] | None = Field(default_factory=list)
    relations: list | None = Field(default_factory=list)
    review_process: list[str] | None = Field(default_factory=list)
    review_processes: list | None = Field(default_factory=list)
    subjects: list[Subject] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)
    waiver: Waiver | None = None

    date_published: str | int | None = Field(None, exclude=True)
    scimago_quartile: str | None = Field(None, exclude=True)
    affiliation_names: list[Name] | None = None

    @model_validator(mode="after")
    def get_scimag_quartile(self):
        if self.ranking:
            for rank in self.ranking:
                if rank.source == "scimago Best Quartile" and rank.rank != "-":
                    self.scimago_quartile = rank.rank
        return self

    class Config:
        json_encoders = {ObjectId: str}