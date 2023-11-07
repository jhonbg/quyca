from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services.jwt import jwt_service
from app.services.user import user_svc
from app.core.config import settings
from app.core.exceptions import InvalidCredentials
from app.protocols.db.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"http://localhost:8000{settings.API_V1_STR}/login/access-token"
)


def get_current_empleado(token: str = Depends(reusable_oauth2)) -> User:
    token_data = jwt_service.decode_access_token(token)
    empleado = user_svc.get(id=token_data.sub)
    if not empleado:
        raise HTTPException(status_code=404, detail="User not found")
    return empleado


def get_current_active_empleado(
    current_empleado: User = Depends(get_current_empleado),
) -> User:
    if not current_empleado.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_empleado


def get_current_active_superempleado(
    current_empleado: User = Depends(get_current_active_empleado),
) -> User:
    if not current_empleado.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a superuser"
        )
    return current_empleado
