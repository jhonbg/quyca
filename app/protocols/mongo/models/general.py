from typing import Protocol, NewType

ObjectId = NewType("ObjectId", str)


class Type(Protocol):
    source: str | None
    type: str | None


class Updated(Protocol):
    time: int | None
    source: str | None


class ExternalId(Protocol):
    id: ObjectId | None | str | int | list[str]
    source: str | None
    provenance: str | None


class ExternalURL(Protocol):
    url: str | int | None
    source: str | None


class Name(Protocol):
    name: str | None
    lang: str | None


class Status(Protocol):
    source: str | None
    status: str | None
