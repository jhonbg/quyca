from enum import Enum


class SessionStatus(str, Enum):
    SESION_NO_INICIADA = "sesion_no_iniciada"
    TOKEN_EXPIRADO = "token_expirado"
    SESION_ACTIVA = "sesion_activa"
