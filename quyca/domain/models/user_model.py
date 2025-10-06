from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str
    institution: str
    ror_id: str | None = None
    rol: str
    token: str
