from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from database.models.base_model import (
    PyObjectId,
    CitationsCount,
    Updated,
    ExternalId,
    Type,
    Identifier,
    Subject,
    Ranking,
)


class Affiliation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: str | None
    position: str | None = None
    start_date: int | str | None
    end_date: int | str | None
    types: list[Type] | None = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}


class BirthPlace(BaseModel):
    city: str | None = None
    country: str | None = None
    state: str | None = None


class Degree(BaseModel):
    id: str | None
    date: str | None
    degree: str | None
    institutions: list | None = Field(default_factory=list)
    source: str | None


class Institution(BaseModel):
    id: str | None
    country_code: str | None
    country_id: str | None
    display_name: str | None
    lineage: list[str] | None = Field(default_factory=list)
    ror: str | None
    type: str | None


class RelatedWork(BaseModel):
    id: str | Identifier | None
    institutions: list[Institution] | None = Field(default_factory=list)
    provenance: str | None
    source: str | None
    year: int | None = None


class Person(BaseModel):
    id: PyObjectId = Field(alias="_id")
    affiliations: list[Affiliation] | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: int | str | None = None
    birthplace: BirthPlace | None = None
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    degrees: list[Degree] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    first_names: list[str] | None = Field(default_factory=list)
    full_name: str | None = Field(serialization_alias="name")
    initials: str | None = None
    keywords: list | None = Field(default_factory=list)
    last_names: list[str] | None = Field(default_factory=list)
    marital_status: str | None = None
    ranking: list[Ranking] | None = Field(default_factory=list)
    related_works: list[RelatedWork] | None = Field(default_factory=list)
    sex: str | None = None
    subjects: list[Subject] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)

    products_count: int | None = None
    logo: str | None = None

    @field_validator("external_ids")
    @classmethod
    def delete_sensitive_external_ids(cls, value):
        return list(
            filter(
                lambda external_id: external_id.source
                not in ["Cédula de Ciudadanía", "Cédula de Extranjería", "Passport"],
                value,
            )
        )

    class Config:
        json_encoders = {ObjectId: str}
