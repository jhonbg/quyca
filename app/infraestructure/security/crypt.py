from passlib.context import CryptContext

from app.core.exceptions import InvalidCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Crypt:
    def check_password(self, plain_password: str, hashed_password: str) -> None:
        verify = pwd_context.verify(plain_password, hashed_password)
        if not verify:
            raise InvalidCredentials("Invalid password")

    def get_password_hash(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)


crypt = Crypt()
