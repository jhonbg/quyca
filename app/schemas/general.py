from typing import TypeVar, Any

from pydantic import BaseModel, validator, Field
from odmantic.bson import BSON_TYPES_ENCODERS

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)

class Type(BaseModel):
    source: str
    type: str


class Updated(BaseModel):
    time: int | None
    source: str | None


class ExternalId(BaseModel):
    id: Any
    source: str | None

class ExternalURL(BaseModel):
    url: str | None
    source: str | None


class Name(BaseModel):
    name: str | None
    lang: str | None


class Status(BaseModel):
    source: str | None
    status: str | None


class QueryBase(BaseModel):
    limit: int = Field(100, gt=0)
    page: int = 1
    keywords: str | None = ""
    sort: str | None = None

    skip: int | None = None

    @validator("limit", always=True)
    def limit_validator(cls, v, values):
        return v if v < 250 else 250

    @validator("skip", always=True)
    def skip_validator(cls, v, values):
        return v if v else (values["page"] - 1) * values["limit"]


class GeneralMultiResponse(BaseModel):
    total_results: int | None
    data: list[Any] | None = Field(default_factory=list)

    class Config:
        json_encoders = {**BSON_TYPES_ENCODERS}
