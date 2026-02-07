
class LogoutUserUseCase:
    def execute(self) -> dict:
        return {"success": True, "msg": "Sesión cerrada correctamente"}
