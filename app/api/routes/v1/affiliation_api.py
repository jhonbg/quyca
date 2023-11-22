import json
from typing import Any

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_api import affiliation_api_service
from utils.encoder import JsonEncoder

router = Blueprint("affiliation_api_v1", __name__)


def affiliation(request: Request) -> dict[str, Any] | None:
    section = request.args.get("section")
    tab = request.args.get("tab")
    data = request.args.get("data")
    idx = request.args.get("id")
    typ = request.args.get("type")

    result = None
    if section == "info":
        result = affiliation_api_service.get_info(idx)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                result = None
            else:
                idx = request.args.get("id")
                start_year = request.args.get("start_year")
                end_year = request.args.get("end_year")
                page = request.args.get("page")
                max_results = request.args.get("max_results")
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


@router.route("", methods=["GET"])
def api_affiliation():
    result = affiliation(request)
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
