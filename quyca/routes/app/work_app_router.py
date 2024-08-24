import json

from flask import Blueprint, Response

from services.work_service import WorkService
from services.work import work_service

work_app_router = Blueprint("work_app_router", __name__)


@work_app_router.route("/<work_id>", methods=["GET"])
def get_work_by_id(work_id: str):
    try:
        work = WorkService.get_work_by_id(work_id)
        exclude_fields = {
            "subtitle": True,
            "titles": True,
            "author_count": True,
            "citations": True,
            "citations_by_year": True,
            "date_published": True,
            "groups": True,
            "keywords": True,
            "ranking": True,
            "references": True,
            "types": True,
            "updated": True,
            "subjects": {'__all__':{"subjects": {"__all__": {"external_ids"}}}},
        }
        return {"data": work.model_dump(exclude=exclude_fields, exclude_none=True)}

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")

@work_app_router.route("/<id>/<section>", methods=["GET"])
def get_work(id: str, section: str | None = "info"):
    if section == "info":
        return work_service.get_info(id=id)
    if section == "authors":
        return work_service.get_authors(id=id)