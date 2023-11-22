from typing import Any

from pydantic import BaseModel, Field

from schemas.general import QueryBase


class Type(BaseModel):
    source: str
    type: str


class Affiliation(BaseModel):
    id: Any
    name: str | None
    types: list[Type] = Field(default_factory=list)
    start_date: int
    end_date: int


class ExternalId(BaseModel):
    id: Any
    source: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Ranking(BaseModel):
    date: str | None
    rank: str | None
    source: str | None


class BirthPlace(BaseModel):
    city: str | None
    state: str | None
    country: str | None


class Degree(BaseModel):
    date: str | int
    degree: str | None
    id: str | None
    intitutions: list[str]
    source: str | None


class Person(BaseModel):
    updated: list[Updated]
    full_name: str | None
    first_names: list[str]
    last_names: list[str]
    initials: str | None
    aliases: list[str]
    affiliations: list[Affiliation] = Field(default_factory=list)
    keywords: list[str]
    external_ids: list[ExternalId]
    sex: str | None
    marital_status: str | None
    ranking: list[Ranking | list[Ranking]]
    birthplace: BirthPlace
    birthdate: int
    degrees: list[Degree]
    subjects: list[Any]


class PersonQueryParams(QueryBase):
    groups: str | None = None
    institutions: str | None = None
    country: str | None = None
    sort: str = "citations"