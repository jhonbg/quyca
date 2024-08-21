from pydantic import BaseModel, field_validator, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, other):
        if value == "":
            return value

        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId '{str(value)}'")

        return str(value)


class Node(BaseModel):
    degree: int
    id: str
    label: str
    size: float


class Edge(BaseModel):
    coauthorships: int
    size: int | float
    source: str
    target: str


class CoauthorshipNetwork(BaseModel):
    nodes: list[Node] | None = Field(default_factory=list)
    edges: list[Edge] | None = Field(default_factory=list)


class TopWord(BaseModel):
    name: str
    value: int

class CitationsCount(BaseModel):
    source: str | None
    count: int | None
    provenance: str | None = None


class Type(BaseModel):
    type_class: str | None = None
    code: str | None = None
    level: int | None = None
    provenance: str | None = None
    source: str | None
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Identifier(BaseModel):
    COD_RH: str | None
    COD_PRODUCTO: str | None = None


class ExternalId(BaseModel):
    id: str | int | list[str] | Identifier | None = None
    provenance: str | None = None
    source: str | None

    @field_validator("id", mode="after")
    @classmethod
    def id_validator(cls, value: str | Identifier):
        if isinstance(value, Identifier) and not value.COD_PRODUCTO:
            value = value.COD_RH

        return value


class ExternalURL(BaseModel):
    url: str | int | None
    source: str | None
    provenance: str | None = None


class Name(BaseModel):
    name: str | None
    lang: str | None
    source: str | None
    provenance: str | None = None


class Ranking(BaseModel):
    date: int | str | None = None
    from_date: int | str | None = None
    issn: str | None = None
    order: str | int | None = None
    rank: str | int | float | None = None
    source: str | None = None
    to_date: int | str | None = None


class Status(BaseModel):
    source: str | None
    status: str | None


class SubjectContent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    level: int | None = None
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Subject(BaseModel):
    provenance: str | None = None
    source: str | None
    subjects: list[SubjectContent] | None = Field(default_factory=list)
