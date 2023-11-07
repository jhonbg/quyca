from app.services.crypt import crypt_svc
from app.services.jwt import jwt_service
from app.infraestructure.security.crypt import crypt
from app.infraestructure.security.jwt import jwt


def init_security() -> None:
    crypt_svc.register_observer(crypt)
    jwt_service.register_observer(jwt)