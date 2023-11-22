from odmantic import EmbeddedModel, ObjectId
from pydantic import BaseModel


class Type(EmbeddedModel):
    source: str | None
    type: str | None


class Updated(EmbeddedModel):
    time: int | None
    source: str | None


class ExternalId(EmbeddedModel):
    id: ObjectId | None | str
    source: str | None


class ExternalURL(EmbeddedModel):
    url: str | None
    source: str | None


class Name(BaseModel):
    name: str | None
    lang: str | None


class Status(BaseModel):
    source: str | None
    status: str | None