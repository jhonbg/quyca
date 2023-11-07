from datetime import timedelta, datetime

from jose import jwt as jose_jwt
from jose.exceptions import JWTError

from app.core.config import settings
from app.core.exceptions import InvalidCredentials
from app.schemas.token import TokenPayload


class JWT:
    def create_access_token(self, subject: str, expires_delta: timedelta = None) -> str:
        if expires_delta:
            expires = datetime.utcnow() + expires_delta
        else:
            expires = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        token = jose_jwt.encode(
            {"exp": expires, "sub": str(subject)},
            str(settings.SECRET_KEY),
            algorithm=settings.ALGORITHM,
        )
        return token

    def decode_access_token(self, token: str) -> TokenPayload:
        try:
            payload = jose_jwt.decode(
                token, str(settings.SECRET_KEY), algorithms=[settings.ALGORITHM]
            )
            return TokenPayload(**payload)
        except JWTError:
            raise InvalidCredentials("Invalid access token")


jwt = JWT()
