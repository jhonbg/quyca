from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str
    institution: str
    rolID: str | None = None
    token: str
