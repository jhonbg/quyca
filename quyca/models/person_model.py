from typing import Any, Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field
from models.base_model import PyObjectId, CitationsCount


class Updated(BaseModel):
    time: Optional[int]
    source: Optional[str]


class Type(BaseModel):
    source: Optional[str]
    type: Optional[str]


class Affiliation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    name: Optional[str]
    types: Optional[List[Type]] = Field(default_factory=List)
    start_date: Optional[int | str]
    end_date: Optional[int | str]
    position: Optional[str] = None


class ExternalId(BaseModel):
    id: Optional[str | dict] = None
    source: Optional[str] = None
    provenance: Optional[str] = None


class Ranking(BaseModel):
    date: Optional[int | str] = None
    rank: Optional[Any | str] = None
    source: Optional[str]
    id: Optional[Any | str] = None
    order: Optional[Any | int] = None


class BirthPlace(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class Degree(BaseModel):
    date: Optional[int | str]
    degree: Optional[str] = ""
    id: Optional[str]
    institutions: Optional[List[str]] = Field(default_factory=List)
    source: Optional[str]


class Person(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    updated: List[Updated]
    full_name: Optional[str] = Field(serialization_alias="name")
    first_names: List[str]
    last_names: List[str]
    external_ids: Optional[List[ExternalId]] = Field(default_factory=list)
    affiliations: List[Affiliation] = Field(default_factory=list)
    initials: Optional[str | List[str]]
    aliases: List[str]
    keywords: List[str]
    sex: Optional[str]
    marital_status: Optional[str]
    ranking: List[Ranking]
    birthplace: BirthPlace
    birthdate: Optional[int | str] = None
    degrees: List[Degree]
    subjects: List[Any]
    citations_count: Optional[List[CitationsCount]] = Field(default_factory=list)
    products_count: Optional[int] = None
    logo: Optional[str] = None

    class Config:
        json_encoders = {
            ObjectId: str
        }
