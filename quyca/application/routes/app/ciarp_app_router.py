from datetime import datetime
from zoneinfo import ZoneInfo
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Blueprint, request, jsonify
from infrastructure.container import build_ciarp_service
from domain.services.ciarp_service import CiarpService

ciarp_app_router = Blueprint("ciarp_app_router", __name__)

@ciarp_app_router.route("/ciarp", methods=["POST"])
def submit_ciarp():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
    except Exception:
        return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401
    
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "msg": "Token inválido o expirado"}), 401
    
    token_from_header = auth_header.split(" ")[1]
    file = request.files.get("file")
    upload_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")
    
    process_usecase, save_usecase, user_repo = build_ciarp_service()
    service = CiarpService(process_usecase, save_usecase, user_repo)
    
    result, status = service.handle_ciarp_upload(file, claims, token_from_header, upload_date)
    return jsonify(result), status