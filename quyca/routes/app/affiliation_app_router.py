import json

from flask import Blueprint, request, Response, jsonify

from database.models.base_model import QueryParams
from services import new_affiliation_service, new_work_service

affiliation_app_router = Blueprint("affiliation_app_router", __name__)


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>", methods=["GET"])
def get_affiliation_by_id(affiliation_type: str, affiliation_id: str):
    try:
        data = new_affiliation_service.get_affiliation_by_id(affiliation_id)
        return Response(json.dumps(data), 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/<section>", methods=["GET"]
)
def get_affiliation_section(affiliation_type: str, affiliation_id: str, section: str):
    if section == "affiliations":
        try:
            data = new_affiliation_service.get_related_affiliations_by_affiliation(
                affiliation_id, affiliation_type
            )
            return Response(json.dumps(data), 200, mimetype="application/json")
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}), 400, mimetype="application/json"
            )
    return Response(
        json.dumps({"error": f"There is no {section} section"}),
        400,
        mimetype="application/json",
    )


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/<section>/<tab>", methods=["GET"]
)
def get_affiliation_section_tab(
    affiliation_id: str, affiliation_type: str, section: str, tab: str
):
    if section == "research" and tab == "products":
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = new_affiliation_service.get_affiliation_plot(
                affiliation_id, affiliation_type, query_params
            )
            return Response(json.dumps(data), 200, mimetype="application/json")
        data = new_affiliation_service.get_works_by_affiliation(
            affiliation_id, affiliation_type
        )
        return Response(json.dumps(data), 200, mimetype="application/json")
    return Response(
        json.dumps({"error": f"There is no {section} section and {tab} tab"}),
        400,
        mimetype="application/json",
    )


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/csv", methods=["GET"]
)
def get_csv_by_affiliation(affiliation_type: str, affiliation_id: str):
    try:
        data = new_work_service.get_works_csv_by_affiliation(
            affiliation_id, affiliation_type
        )
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
