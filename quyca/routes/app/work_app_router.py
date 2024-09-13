import json

from flask import Blueprint, jsonify

from services import new_work_service

work_app_router = Blueprint("work_app_router", __name__)


@work_app_router.route("/<work_id>", methods=["GET"])
def get_work_by_id(work_id: str):
    try:
        data = new_work_service.get_work_by_id(work_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@work_app_router.route("/<work_id>/authors", methods=["GET"])
def get_work_authors(work_id: str):
    try:
        data = new_work_service.get_work_authors(work_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
