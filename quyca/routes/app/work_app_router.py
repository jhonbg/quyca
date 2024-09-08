import json

from flask import Blueprint, Response

from services import new_work_service
from services.work import work_service

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


@work_app_router.route("/<id>/<section>", methods=["GET"])
def get_work(id: str, section: str | None = "info"):
    if section == "info":
        return work_service.get_info(id=id)
    if section == "authors":
        return work_service.get_authors(id=id)
