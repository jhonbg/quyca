from app.services.base import ServiceBase
from app.services.crypt import crypt_svc
from app.schemas.user import UserUpdate, UserCreate, UserCreateInDB, UserInDB
from app.protocols.db.models.user import User
from app.protocols.db.crud.user import CRUDUserProtocol
from app.core.exceptions import InvalidCredentials


class UserService(ServiceBase[User, UserCreateInDB, UserUpdate, CRUDUserProtocol]):
    def create(self, *, obj_in: UserCreate) -> User:
        hashed_password = crypt_svc.get_password_hash(obj_in.password)
        obj = UserCreateInDB(
            **obj_in.dict(
                exclude={
                    "password",
                }
            ),
            hashed_password=hashed_password
        )
        return super().create(obj_in=obj)

    def authenticate(self, *, email: str, password: str) -> UserInDB:
        user = self.observer.get_by_email(email=email)
        crypt_svc.check_password(password, user.hashed_password)
        return user


user_svc = UserService()
