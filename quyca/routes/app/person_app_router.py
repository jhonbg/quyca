import json

from bson.errors import InvalidId
from flask import Blueprint, request, Response, Request

from database.models.base_model import QueryParams
from exceptions.person_exception import PersonException
from services.person import person_service
from services import new_person_service, new_work_service
from services.work import work_service
from schemas.work import WorkQueryParams
from utils.encoder import JsonEncoder

person_app_router = Blueprint("person_app_router", __name__)


@person_app_router.route("/<person_id>", methods=["GET"])
def get_person_by_id(person_id: str):
    try:
        person_model = new_person_service.get_person_by_id(person_id)

        return Response(
            response=json.dumps(
                {"data": person_model.model_dump(by_alias=True), "filters": {}}
            ),
            status=200,
            mimetype="application/json",
        )

    except (PersonException, InvalidId, ValueError) as e:
        return Response(
            response=json.dumps({"error": str(e)}),
            status=404,
            mimetype="application/json",
        )


@person_app_router.route("/<person_id>/<section>/<tab>", methods=["GET"])
def get_person_section_tab(person_id: str, section: str, tab: str):
    if section == "research" and tab == "products":
        query_params = QueryParams(**request.args)
        if query_params.plot:
            return new_person_service.get_person_plot(person_id, query_params)
        data = new_work_service.get_works_by_person(person_id, query_params)
        return Response(json.dumps(data), 200, mimetype="application/json")
    return Response(
        json.dumps({"error": f"There is no {section} section and {tab} tab"}),
        400,
        mimetype="application/json",
    )


@person_app_router.route("/<person_id>/csv", methods=["GET"])
def get_csv_by_person(person_id: str):
    try:
        data = new_work_service.get_works_csv_by_person(person_id)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
