from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel


CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ObjInDB = TypeVar("ObjInDB", bound=BaseModel)


class GeneralResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True