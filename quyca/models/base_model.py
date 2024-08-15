from typing import Optional
from pydantic import BaseModel
from bson import ObjectId, errors


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):

        yield cls.validate

    @classmethod
    def validate(cls, value, other):
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId '{str(value)}'")

        return str(value)


class CitationsCount(BaseModel):
    source: Optional[str]
    count: Optional[int]