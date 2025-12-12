from typing import Any, Dict, Tuple

from werkzeug.datastructures import FileStorage
from infrastructure.notifications.notification import StaffNotification
from infrastructure.repositories.user_repository import UserRepositoryMongo

ALLOWED_COMPRESSED_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".tar.gz",
    ".tar.bz2",
}

class ScientiService:
    """
    Domain service for managing the upload of SCIENTI compressed files.
    """
    
    def __init__(
        self,
        notification: StaffNotification,
        user_repo: UserRepositoryMongo,
        ) -> None:
        self.notification = notification,
        self.user_repo = user_repo
    
    def _is_compressed_file(self, filename: str) -> bool:
        filename_lower = filename.lower()
        for ext in ALLOWED_COMPRESSED_EXTENSIONS:
            if filename_lower.endswith(ext):
                return True
        return False
    
    def handle_scienti_upload(
        self,
        file: FileStorage | None,
        claims: dict[str, Any],
        token: str,
        upload_date: str,
    ) -> Tuple[Dict[str, Any], int]:
        email = claims.get("sub")
        ror_id = claims.get("_id")
        institution = claims.get("institution")
        rol = claims.get("rol")
        
        if not self.user_repo.is_token_valid(email, token):
            return {
                "success": False,
                "msg": "Token inválido o revocado"
            }, 401
        
        if file is None or not isinstance(file, FileStorage):
            return {"success": False, "msg": "Archivo requerido"}, 400
        
        filename = file.filename or ""
        if not filename:
            return {"success": False, "msg": "Nombre de archivo inválido"}, 400
        
        if not self._is_compressed_file(filename):
            return {
                "success": False,
                "msg": "Tipo de archivo no permitido. Los formatos soportados son: .zip, .rar, .7z, .tar, .gz, .tgz, .bz2, .tar.gz y .tar.bz2."
            }, 415
            
        notify_result = self.notification.send_scienti_compressed_received(
            rol=str(rol),
            institution=institution,
            filename=filename,
            upload_date=upload_date,
            email=email,
            ror_id=ror_id,
        )
        
        if not notify_result.get("success", False):
            return {
                "success": False,
                "msg": "Fallo al enviar correo de confirmación",
                "email_error": notify_result,
            },500
        
        return {
            "success": True,
            "msg": "Archivo SCIENTI recibido con éxito para ser validado.",
            "filename": filename,
            "upload_date": upload_date,
        }, 200