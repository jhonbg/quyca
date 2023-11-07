from typing import Protocol


class CryptProtocol(Protocol):
    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        ...

    def get_password_hash(self, plain_password: str) -> str:
        ...
