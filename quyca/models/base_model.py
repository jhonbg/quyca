from typing import Optional
from pydantic import BaseModel, field_validator, Field
from bson import ObjectId, errors


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
    source: Optional[str]
    count: Optional[int]


class Type(BaseModel):
    source: str
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Identifier(BaseModel):
    COD_RH: str | None = None
    COD_PRODUCTO: str | None = None


class ExternalId(BaseModel):
    id: str | int | list[str] | Identifier | None = None
    source: str | None

    @field_validator("id", mode="after")
    @classmethod
    def id_validator(cls, value: str | int | list[str] | dict | Identifier):
        if isinstance(value, dict):
            id = []
            id += [value.get("COD_RH")] if isinstance(value.get("COD_RH", None), str) else []
            id += (
                [value.get("COD_PRODUCTO")]
                if isinstance(value.get("COD_PRODUCTO", None), str)
                else []
            )
            return "-".join(id)
        if isinstance(value, Identifier):
            id = []
            id += [value.COD_RH] if isinstance(value.COD_RH, str) else []
            id += [value.COD_PRODUCTO] if isinstance(value.COD_PRODUCTO, str) else []
            return "-".join(id)
        return value


class ExternalURL(BaseModel):
    url: str | int | None
    source: str | None


class Name(BaseModel):
    name: str | None
    lang: str | None


class Status(BaseModel):
    source: str | None
    status: str | None
