from typing import TypeVar, Any, Generic

from pydantic import BaseModel, validator, Field, model_validator
from odmantic.bson import BSON_TYPES_ENCODERS
from core.config import settings

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)


class Type(BaseModel):
    source: str
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Identifier(BaseModel):
    COD_RH: str


class ExternalId(BaseModel):
    id: str | int | list[str] | Identifier | None = None
    source: str | None
    provenance: str | None = None

    @validator("id", pre=True)
    def id_validator(cls, v: str | int | list[str] | Identifier | None):
        return v.get("COD_RH", None) if isinstance(v, dict) else v


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
    page: int = Field(1, gt=0)
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

    def next_query(self) -> str:
        return (
            f"max={self.max}&page={self.page + 1}&"
            f"sort={self.sort}&keywords={self.keywords}"
        )

    def previous_query(self) -> str | None:
        return (
            f"max={self.max}&page={self.page - 1}&"
            f"sort={self.sort}&keywords={self.keywords}"
        )

    def get_cursor(self, path: str) -> dict[str, str]:
        """
        Compute the cursor for the given path and query.
        """
        return {
            "next": f"{settings.APP_DOMAIN}{path}?{self.next_query()}",
            "previous": (
                f"{settings.APP_DOMAIN}{path}?{self.previous_query()}"
                if self.page > 1
                else None
            ),
        }


class GeneralMultiResponse(BaseModel, Generic[DBSchemaType]):
    total_results: int | None = None
    data: list[DBSchemaType] | None = Field(default_factory=list)
    count: int | None = None
    page: int | None = None

    model_config = {"json_encoders": BSON_TYPES_ENCODERS}
