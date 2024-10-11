from typing import Tuple

from flask import Blueprint, jsonify, Response

from domain.services import other_work_service

other_work_app_router = Blueprint("other_work_app_router", __name__)


@other_work_app_router.route("/<other_work_id>", methods=["GET"])
def get_other_work_by_id(other_work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = other_work_service.get_other_work_by_id(other_work_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@other_work_app_router.route("/<other_work_id>/authors", methods=["GET"])
def get_other_work_authors(other_work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = other_work_service.get_other_work_authors(other_work_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
