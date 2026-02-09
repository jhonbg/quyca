from datetime import datetime
from typing import Any, Tuple
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from sentry_sdk import capture_exception

from quyca.infrastructure.container import build_scienti_service
from quyca.domain.services.scienti_service import ScientiService

scienti_app_router = Blueprint("scienti_app_router", __name__)

"""
@api {post} /app/submit/scienti Carga de archivo comprimido SCIENTI
@apiName PostScientiUpload
@apiGroup SCIENTI
@apiVersion 1.0.0
@apiDescription
Permite cargar un archivo <b>comprimido</b> asociado al sistema SCIENTI.
Este endpoint:
- Verifica el token JWT y su validez.
- Valida que el archivo exista y sea un formato comprimido permitido.
- Envía un correo de confirmación indicando que los datos fueron recibidos
    con éxito para ser validados.
No se procesa ni valida el contenido del archivo en este endpoint.

@apiHeader {String} Authorization Token JWT en formato `Bearer &lt;token&gt;`.

@apiBody {File} file Archivo comprimido a enviar.

@apiSuccess {Boolean} success Indica si el proceso fue exitoso.
@apiSuccess {String} msg Mensaje de confirmación.
@apiSuccess {String} filename Nombre del archivo recibido.
@apiSuccess {String} upload_date Fecha y hora de recepción (zona America/Bogota).
"""


@scienti_app_router.route("/scienti", methods=["POST"])
def submit_scienti() -> Tuple[Response, int]:
    try:
        try:
            verify_jwt_in_request()
            claims: dict[str, Any] = get_jwt()
        except Exception:
            return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401

        file = request.files.get("file")
        if file is None:
            return jsonify({"sucess":False, "msg": "Archivo requerido"}), 400
        
        upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        service: ScientiService = build_scienti_service()

        result, status = service.handle_scienti_upload(
            file=file, claims=claims, upload_date=upload_date
        )

        return jsonify(result), status
    except Exception as e:
        capture_exception(e)
        return jsonify({"success": False, "msg": "Error interno del servidor"}), 500
