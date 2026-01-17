from typing import Protocol, Any


class ITokenService(Protocol):
    def create_access_token(self, subject: str, claims: dict[str, Any]) -> str: ...

    def decode(self, token: str) -> dict[str, Any]: ...
