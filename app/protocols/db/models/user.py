from app.protocols.db.utils.model import BaseModel


class User(BaseModel):
    email: str
    names: str | None
    last_names: str | None
    address: str | None
    age: int | None
    hashed_password: str
    is_superuser: bool | None
    active: bool | None
