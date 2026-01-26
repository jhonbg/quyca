from quyca.domain.auth.auth_ports import ITokenSessionRepository
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo


class TokenSessionRepositoryMongo(ITokenSessionRepository):
    def __init__(self, user_repo: UserRepositoryMongo) -> None:
        self.user_repo = user_repo

    def is_token_valid(self, email: str, token: str) -> bool:
        return self.user_repo.is_token_valid(email, token)
