from __future__ import annotations

import io
from typing import Any
from quyca.application.usecases.process_staff_file import ProcessStaffFileUseCase
from quyca.application.usecases.save_staff_file import SaveStaffFileUseCase
from quyca.infrastructure.repositories.user_repository import UserRepositoryMongo
from werkzeug.datastructures import FileStorage


class StaffService:
    """
    Application service orchestrating Staff upload flow (auth → process → persist).
    """

    def __init__(
        self,
        process_usecase: ProcessStaffFileUseCase,
        save_usecase: SaveStaffFileUseCase,
        user_repo: UserRepositoryMongo,
    ):
        self.process_usecase = process_usecase
        self.save_usecase = save_usecase
        self.user_repo = user_repo

    def handle_staff_upload(
        self, file: FileStorage, claims: dict[str, Any], token: str, upload_date: str
    ) -> tuple[dict, int]:
        email = claims.get("sub")
        ror_id = claims.get("_id")
        institution = claims.get("institution")
        user = claims.get("rol")

        if (
            not isinstance(email, str)
            or not isinstance(ror_id, str)
            or not isinstance(institution, str)
            or not isinstance(user, str)
            or not email
            or not ror_id
            or not institution
            or not user
        ):
            return {"success": False, "msg": "Token inválido o revocado"}, 401

        if not self.user_repo.is_token_valid(email, token):
            return {"success": False, "msg": "Token inválido o revocado"}, 401

        if not file:
            return {"success": False, "msg": "Archivo requerido"}, 400

        filename = file.filename or ""
        if not filename:
            return {"success": False, "msg": "Archivo requerido"}, 400

        file.stream.seek(0)
        file_bytes = io.BytesIO(file.stream.read())
        file_bytes.seek(0)

        result = self.process_usecase.execute(
            file_bytes,
            institution,
            filename,
            upload_date,
            user,
            email,
            ror_id,
        )

        if not result["success"]:
            if result.get("msg", "").startswith("El archivo enviado no cumple con el formato requerido de columnas"):
                return result, 422
            return result, 400

        file.stream.seek(0)
        save_result = self.save_usecase.execute(file, ror_id, institution)

        result.update({"file_msg": save_result.get("msg")})
        return result, 200
