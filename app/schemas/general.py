from typing import TypeVar, Any, Generic

from pydantic import BaseModel, validator, Field, model_validator
from odmantic.bson import BSON_TYPES_ENCODERS

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)

class Type(BaseModel):
    source: str
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class ExternalId(BaseModel):
    id: Any | None = None
    source: str | None
    provenance: str | None = None

class ExternalURL(BaseModel):
    url: str | int | None
    source: str | None


class Name(BaseModel):
    name: str | None
    lang: str | None


class Status(BaseModel):
    source: str | None
    status: str | None


class QueryBase(BaseModel):
    max: int = Field(10, gt=0)
    page: int = 1
    keywords: str | None = ""
    sort: str = ""

    skip: int | None = None

    @validator("max", always=True)
    def limit_validator(cls, v, values):
        return v if v < 250 else 250

    @validator("skip", always=True)
    def skip_validator(cls, v, values):
        return v if v else (values["page"] - 1) * values["max"]
    
    @property
    def get_search(self) -> dict[str, Any]:
        return {}


class GeneralMultiResponse(BaseModel, Generic[DBSchemaType]):
    total_results: int | None = None
    data: list[DBSchemaType] | None = Field(default_factory=list)
    count: int | None = None
    page: int | None = None
    
    model_config = {"json_encoders": BSON_TYPES_ENCODERS}
