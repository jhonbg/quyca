from typing import TypeVar, Type
from datetime import timedelta

from app.protocols.security.jwt import JWT
from app.core.exceptions import NoObserverRegister
from app.schemas.token import TokenPayload


JWTType = TypeVar("JWTType", bound=JWT)


class JWTService:
    def __init__(self):
        self.observer: Type[JWTType] | None = None

    def register_observer(self, observer: Type[JWTType]) -> None:
        self.observer = observer
        return None

    def unregister_observer(self) -> None:
        self.observer = None
        return None

    def create_access_token(self, subject: str, expires: int | None) -> str:
        if not self.observer:
            raise NoObserverRegister(self.__class__.__name__)
        return self.observer.create_access_token(
            subject, timedelta(hours=expires) if expires else None
        )

    def decode_access_token(self, token: str) -> TokenPayload:
        if not self.observer:
            raise NoObserverRegister(self.__class__.__name__)
        return self.observer.decode_access_token(token)


jwt_service = JWTService()