from typing import Protocol, Any


class IJwtCookieReader(Protocol):
    def get_access_token(self) -> str | None: ...


class IJwtVerifier(Protocol):
    def verify_from_cookies(self) -> dict[str, Any] | None: ...


class ITokenSessionRepository(Protocol):
    def is_token_valid(self, email: str, token: str) -> bool: ...
