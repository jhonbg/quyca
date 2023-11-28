import json

from flask import Blueprint, request, Response

from services.v1.person_api import person_api_service
from utils.encoder import JsonEncoder

router = Blueprint("person_api_v1", __name__)


@router.route("/<id>", methods=["GET"])
def get_person(id: str | None):
    data = request.args.get("data")

    if data == "info":
        result = person_api_service.get_info(id)
    elif data == "production":
        max_results = request.args.get("max")
        page = request.args.get("page")
        start_year = request.args.get("start_year")
        end_year = request.args.get("end_year")
        sort = request.args.get("sort")
        result = person_api_service.get_production(
            idx=id,
            max_results=max_results,
            page=page,
            start_year=start_year,
            end_year=end_year,
            sort=sort,
            direction="ascending",
        )
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
