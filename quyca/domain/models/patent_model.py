from bson import ObjectId
from pydantic import BaseModel, Field

from domain.models.base_model import (
    PyObjectId,
    Type,
    ExternalId,
    ExternalUrl,
    Updated,
    Ranking,
    Author,
    Group,
    Title,
    ProductType,
)


class Patent(BaseModel):
    id: PyObjectId = Field(alias="_id")
    author_count: int | None = None
    authors: list[Author] | str | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    groups: list[Group] | str | None = None
    ranking: list[Ranking] | str | None = None
    titles: list[Title] | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None

    authors_data: list[Author] | None = None
    language: str | None = None
    product_types: list[ProductType] | None = None
    title: str | None = None

    class Config:
        json_encoders = {ObjectId: str}
