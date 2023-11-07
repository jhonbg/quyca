from typing import TypeVar, Type

from app.protocols.security.crypt import CryptProtocol
from app.core.exceptions import NoObserverRegister


CryptType = TypeVar("CryptType", bound=CryptProtocol)


class CryptService:
    def __init__(self):
        self.observer: Type[CryptType] | None = None

    def register_observer(self, observer: Type[CryptType]) -> None:
        self.observer = observer
        return None

    def unregister_observer(self) -> None:
        self.observer = None
        return None

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        if self.observer is None:
            raise NoObserverRegister(service=self.__class__.__name__)
        return self.observer.check_password(plain_password, hashed_password)

    def get_password_hash(self, plain_password: str) -> str:
        if self.observer is None:
            raise NoObserverRegister(service=self.__class__.__name__)
        return self.observer.get_password_hash(plain_password)


crypt_svc = CryptService()
