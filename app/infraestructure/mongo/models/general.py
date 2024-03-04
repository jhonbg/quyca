from odmantic import EmbeddedModel, ObjectId
from odmantic.bson import BaseBSONModel


class Type(EmbeddedModel):
    source: str | None
    type: str | None


class Updated(EmbeddedModel):
    time: int | None
    source: str | None


class ExternalId(EmbeddedModel):
    id: ObjectId | None | str | int
    source: str | None


class ExternalURL(EmbeddedModel):
    url: str | int | None
    source: str | None


class Name(BaseBSONModel):
    name: str | None
    lang: str | None


class Status(BaseBSONModel):
    source: str | None
    status: str | None
