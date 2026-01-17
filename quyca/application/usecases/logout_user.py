from quyca.application.ports.token_service import ITokenService
from quyca.domain.repositories.user_repository_interface import IUserRepository


class LogoutUserUseCase:
    def __init__(self, user_repo: IUserRepository, token_service: ITokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    def execute(self, token: str) -> dict:
        if not token:
            return {"success": False, "msg": "Token requerido"}

        try:
            decoded = self.token_service.decode(token)
            email = decoded.get("sub")

            if not email:
                return {"success": False, "msg": "Problema en el token"}

            removed = self.user_repo.remove_token(email, token)

            if not removed:
                return {"success": False, "msg": "Token inválido o caducado"}

            return {"success": True, "msg": "Sesión cerrada correctamente"}

        except Exception:
            return {"success": False, "msg": "Se presentó un error interno. Intenta nuevamente más tarde."}
