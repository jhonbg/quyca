from odmantic import EmbeddedModel
from odmantic.bson import BaseBSONModel
from pydantic import BaseModel


class CitationsCount(EmbeddedModel):
    source: str | None = None
    count: int | None = None


class Type(EmbeddedModel):
    source: str | None = None
    type: str | None = None


class Updated(EmbeddedModel):
    time: int | None = None
    source: str | None = None


class Identifier(BaseModel):
    COD_RH: str | None = None
    COD_PRODUCTO: str | None = None


class ExternalId(EmbeddedModel):
    id: str | int | list[str] | Identifier | None = None
    source: str | None = None
    provenance: str | None = None


class ExternalURL(EmbeddedModel):
    url: str | int | None = None
    source: str | None = None


class Name(BaseBSONModel):
    name: str | None = None
    lang: str | None = None


class Status(BaseBSONModel):
    source: str | None = None
    status: str | None = None
