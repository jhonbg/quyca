from flask import Blueprint

from services.work import work_service

work_app_router = Blueprint("work_app_router", __name__)


@work_app_router.route("/<id>", methods=["GET"])
@work_app_router.route("/<id>/<section>", methods=["GET"])
def get_work(id: str, section: str | None = "info"):
    if section == "info":
        return work_service.get_info(id=id)
    if section == "authors":
        return work_service.get_authors(id=id)