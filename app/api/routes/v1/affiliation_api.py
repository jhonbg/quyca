import json
from typing import Any

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_api import affiliation_api_service
from services.work import work_service
from utils.encoder import JsonEncoder
from schemas.general import QueryBase
from core.config import settings

router = Blueprint("affiliation_api_v1", __name__)


def affiliation(
    request: Request,
    *,
    idx: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
    typ: str | None = None,
) -> dict[str, Any] | None:
    result = None
    if section == "info":
        result = affiliation_api_service.get_info(idx)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                result = None
            else:
                params = QueryBase(**request.args)
                result = work_service.get_research_products_info_by_affiliation_csv(
                    affiliation_id=idx,
                    affiliation_type=typ,
                    skip=params.skip,
                    limit=params.max,
                    sort=params.sort,
                )
                total = work_service.count_papers(
                    affiliation_id=idx, affiliation_type=typ
                )
                return {
                    "data": result,
                    "info": {
                        "total_products": total,
                        "count": len(result),
                        "cursor": params.get_cursor(
                            path=f"{settings.API_V1_STR}/affiliation/{typ}/{idx}/research/products"
                        ),
                    },
                }
    else:
        result = None
    return {"date": result}


@router.route("/<typ>/<id>", methods=["GET"])
@router.route("/<typ>/<id>/<section>", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>", methods=["GET"])
def api_affiliation(
    id: str | None,
    section: str | None = "info",
    tab: str | None = None,
    typ: str | None = None,
):
    result = affiliation(request, idx=id, section=section, tab=tab, typ=typ)
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
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
