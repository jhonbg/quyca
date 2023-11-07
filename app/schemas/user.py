from pydantic import BaseModel, Field, EmailStr

from app.schemas.model import GeneralResponse


class UserBase(BaseModel):
    email: EmailStr
    names: str | None
    last_names: str | None
    address: str | None
    age: int | None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: str | None
    names: str | None
    last_names: str | None
    address: str | None
    age: int | None


class UserCreateInDB(UserBase):
    hashed_password: str


class UserInDB(GeneralResponse, UserBase):
    ...


class UserSearch(BaseModel):
    names__icontains: str | None = Field(None, alias="names")
    email__icontains: str | None = Field(None, alias="email")

    class Config:
        allow_population_by_field_name = True