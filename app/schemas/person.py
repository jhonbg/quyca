from typing import Any

from pydantic import BaseModel, Field, field_validator

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


class PersonBase(BaseModel):
    full_name: str | None
    external_ids: list[ExternalId] = Field(default_factory=list)
    affiliations: list[Affiliation] = Field(default_factory=list)


class Person(PersonBase):
    updated: list[Updated]
    first_names: list[str]
    last_names: list[str]
    initials: str | None
    aliases: list[str]
    keywords: list[str]
    sex: str | None
    marital_status: str | None
    ranking: list[Ranking | list[Ranking]]
    birthplace: BirthPlace
    birthdate: int
    degrees: list[Degree]
    subjects: list[Any]


class PersonSearch(PersonBase):
    @field_validator("external_ids")
    @classmethod
    def remove_sensitive_ids(cls, v: list[ExternalId]) -> list[ExternalId]:
        return list(
            filter(
                lambda x: x.source
                not in [
                    "Cédula de Ciudadanía",
                    "Cédula de Extranjería",
                    "Passport",
                ],
                v,
            )
        )


class PersonQueryParams(QueryBase):
    groups: str | None = None
    institutions: str | None = None
    country: str | None = None
    sort: str = ""

    @property
    def get_search(self) -> dict[str, Any]:
        return {"external_ids": {"$ne": []}}
