from pydantic import BaseModel, field_validator, Field, conint
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
    source: str | None = None

    @field_validator("id", mode="after")
    @classmethod
    def id_validator(cls, value: str | int | list[str] | Identifier | None) -> str:
        if isinstance(value, Identifier):
            if value.COD_PRODUCTO:
                value = value.COD_RH + "-" + value.COD_PRODUCTO
            else:
                value = value.COD_RH
        return value

    def __hash__(self):
        return hash(str(self.id) + str(self.source))


class ExternalUrl(BaseModel):
    url: str | int | None = None
    source: str | None = None
    provenance: str | None = None

    def __hash__(self):
        return hash(str(self.url) + str(self.source))


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
    id: PyObjectId = None
    external_ids: list[ExternalId] | None = None
    level: int | None = None
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Subject(BaseModel):
    provenance: str | None = None
    source: str | None
    subjects: list[SubjectContent] | None = None


class Address(BaseModel):
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    lat: float | str | None = None
    lng: float | str | None = None
    postcode: str | None = None
    state: str | None = None


class Publisher(BaseModel):
    id: str | None = None
    country_code: str | None = None
    name: str | float | None = None


class APC(BaseModel):
    charges: int | None = None
    currency: str | None = None
    year_published: int | None = None


class QueryParams(BaseModel):
    limit: conint(ge=1) = Field(default=None, alias="max")
    page: conint(ge=1) = None
    keywords: str = None
    plot: str = None
    sort: str = None
