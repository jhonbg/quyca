from dataclasses import dataclass
from typing import Any

from quyca.domain.auth.session_status import SessionStatus
from quyca.domain.auth.auth_ports import IJwtCookieReader, IJwtVerifier


@dataclass(frozen=True)
class MeResult:
    status: SessionStatus
    msg: str
    user: dict[str, Any] | None = None


class GetMeUseCase:
    def __init__(
        self,
        cookie_reader: IJwtCookieReader,
        jwt_verifier: IJwtVerifier,
    ) -> None:
        self.cookie_reader = cookie_reader
        self.jwt_verifier = jwt_verifier

    def execute(self) -> MeResult:
        token = self.cookie_reader.get_access_token()
        if not token:
            return MeResult(SessionStatus.SESION_NO_INICIADA, "Sesión no iniciada")

        claims = self.jwt_verifier.verify_from_cookies()
        if not claims:
            return MeResult(SessionStatus.TOKEN_EXPIRADO, "Token expirado o inválido")

        email = claims.get("sub")
        if not isinstance(email, str) or not email.strip():
            return MeResult(SessionStatus.TOKEN_EXPIRADO, "Token revocado o inválido")

        return MeResult(
            SessionStatus.SESION_ACTIVA,
            "Sesión activa",
            user={
                "_id": claims.get("_id"),
                "institution": claims.get("institution"),
                "role": claims.get("role"),
                "email": email,
            },
        )
