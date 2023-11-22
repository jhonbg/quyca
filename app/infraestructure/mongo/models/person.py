from typing import Any

from odmantic import Model, EmbeddedModel, Field
from pydantic import validator

from infraestructure.mongo.models.general import Type, Updated, ExternalId


class Affiliation(EmbeddedModel):
    id: Any
    name: str | None
    types: list[Type] | None = Field(default_factory=list)
    start_date: int | str | None
    end_date: int | str | None
    position: Any


class Ranking(EmbeddedModel):
    date: str | None
    rank: str | None
    source: str | None


class BirthPlace(EmbeddedModel):
    city: str | None
    state: str | None
    country: str | None


class Degree(EmbeddedModel):
    date: str | int | None
    degree: str | None
    id: str | None
    institutions: list[str] | None = Field(default_factory=list)
    source: str | None


class Person(Model):
    updated: list[Updated]
    full_name: str | None
    first_names: list[str]
    last_names: list[str]
    initials: str | list[str] | None
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

    class Config:
        collection = "person"

    @validator("external_ids")
    def source_validator(cls, v: list[ExternalId], values):
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
