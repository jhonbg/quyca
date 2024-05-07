import json

from flask import Blueprint, request, Response

from services.v1.person_api import person_api_service
from services.work import work_service
from utils.encoder import JsonEncoder
from schemas.general import QueryBase
from core.config import settings

router = Blueprint("person_api_v1", __name__)


@router.route("/<id>/<section>/<tab>", methods=["GET"])
def get_person(id: str | None, section: str | None, tab: str | None):

    if section == "info":
        result = person_api_service.get_info(id)
    elif section == "research" and tab == "products":
        params = QueryBase(**request.args)
        works = work_service.get_research_products_by_author_csv(
            author_id=id, sort=params.sort, skip=params.skip, limit=params.max
        )
        total = work_service.count_papers(author_id=id)
        result = {
            "data": works,
            "info": {
                "total_products": total,
                "count": len(works),
                "cursor": params.get_cursor(
                    path=f"{settings.API_V1_STR}/person/{id}/research/products"
                ),
            },
        }
    else:
        result = None

    if result:
        response = Response(
            response=json.dumps(result, cls=JsonEncoder),
            status=200,
            mimetype="application/json",
        )
    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )
    return response
