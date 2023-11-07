from app.protocols.db.crud.base import CRUDProtocol
from app.protocols.db.models.user import User
from app.schemas.user import UserCreateInDB, UserUpdate


class CRUDUserProtocol(CRUDProtocol[User, UserCreateInDB, UserUpdate]):
    def get_by_email(self, *, email: str) -> User:
        ...