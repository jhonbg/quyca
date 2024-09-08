import json

from flask import Blueprint, Response

from services import new_work_service

work_app_router = Blueprint("work_app_router", __name__)


@work_app_router.route("/<work_id>", methods=["GET"])
def get_work_by_id(work_id: str):
    try:
        data = new_work_service.get_work_by_id(work_id)
        return Response(
            response=json.dumps(data), status=200, mimetype="application/json"
        )
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@work_app_router.route("/<work_id>/<section>", methods=["GET"])
def get_work(work_id: str, section: str):
    try:
        if section == "authors":
            data = new_work_service.get_work_authors(work_id)
            return Response(
                response=json.dumps(data), status=200, mimetype="application/json"
            )
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
