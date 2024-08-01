from flask import Blueprint

from services.work import work_service

router = Blueprint("work_app_v1", __name__)


@router.route("/<id>", methods=["GET"])
@router.route("/<id>/<section>", methods=["GET"])
def get_work(id: str, section: str | None = "info"):
    if section == "info":
        return work_service.get_info(id=id)
    if section == "authors":
        return work_service.get_authors(id=id)