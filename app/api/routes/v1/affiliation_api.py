import json
from typing import Any

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_api import affiliation_api_service
from utils.encoder import JsonEncoder

router = Blueprint("affiliation_api_v1", __name__)


def affiliation(
    request: Request,
    *,
    idx: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
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
                start_year = request.args.get("start_year")
                end_year = request.args.get("end_year")
                page = request.args.get("page")
                max_results = request.args.get("max")
                sort = request.args.get("sort")
                result = affiliation_api_service.get_production(
                    idx=idx,
                    start_year=start_year,
                    end_year=end_year,
                    page=page,
                    max_results=max_results,
                    sort=sort,
                )
    else:
        result = None
    return result


@router.route("/<typ>/<id>", methods=["GET"])
@router.route("/<typ>/<id>/<section>", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>", methods=["GET"])
def api_affiliation(
    id: str | None,
    section: str | None = "info",
    tab: str | None = None,
    typ: str | None = None,
):
    result = affiliation(request, idx=id, section=section, tab=tab)
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
