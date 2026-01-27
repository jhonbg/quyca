from quyca.domain.models.user_model import User
from quyca.infrastructure.mongo import impactu_database
from quyca.infrastructure.security.password_hasher import verify_password
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.repositories.user_repository_interface import IUserRepository

"""
MongoDB repository for login + token management.
"""


class UserRepositoryMongo(IUserRepository):
    """Initializes Mongo collection handle."""

    def __init__(self) -> None:
        self.collection = impactu_database["users"]

    """Validates credentials and returns a user or raises error."""

    def get_by_email_and_pass(self, email: str, password: str) -> User:
        email = email.strip().lower()

        user_data = self.collection.find_one(
            {"email": email.strip().lower()},
            {"password": 1, "email": 1, "institution": 1, "role": 1, "token": 1, "is_active": 1, "apikey": 1},
        )

        if not user_data:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")

        stored_hash = user_data.get("password")
        try:
            if not stored_hash or not verify_password(password, stored_hash):
                raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")
        except Exception:
            raise NotEntityException(f"Usuario con correo {email} no encontrado o contraseña no conciden")

        return User(
            id=str(user_data["_id"]),
            email=user_data["email"],
            institution=user_data["institution"],
            role=user_data["role"],
            token=user_data.get("token"),
            is_active=user_data.get("is_active", True),
            apikey=user_data.get("apikey"),
        )

    """Stores or refreshes the latest token for a user."""

    def update_token(self, email: str, token: str) -> None:
        self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": token}})

    """Clears token if it matches the stored one."""

    def remove_token(self, email: str, token: str) -> bool:
        user = self.collection.find_one({"email": email.strip().lower()}, {"password": 0})
        if user and user.get("token") == token:
            self.collection.update_one({"email": email.strip().lower()}, {"$set": {"token": ""}})
            return True
        return False

    """Checks if the given token is currently valid for the user."""

    def is_token_valid(self, email: str, token: str) -> bool:
        user = self.collection.find_one({"email": email.strip().lower()}, {"password": 0})
        return user is not None and user.get("token") == token
