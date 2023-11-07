from typing import Protocol
from datetime import timedelta

from app.schemas.token import TokenPayload


class JWT(Protocol):
    def create_access_token(self, subject: str, expires_delta: timedelta = None) -> str:
        ...

    def decode_access_token(self, token: str) -> TokenPayload:
        ...
