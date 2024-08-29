import json

from flask import Blueprint, request, Response, jsonify
from pydantic import ValidationError

from services.affiliation import affiliation_service
from schemas.work import WorkQueryParams
from services import new_affiliation_service
from utils.encoder import JsonEncoder
from utils.flatten_json import flatten_json_list

affiliation_app_router = Blueprint("affiliation_app_router", __name__)


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>", methods=["GET"])
def get_affiliation_by_id(affiliation_type: str, affiliation_id: str):
    try:
        affiliation = new_affiliation_service.get_by_id(affiliation_id)
        response_data = json.dumps(
            {"data": affiliation.model_dump(by_alias=True), "filters": {}}
        )

        return Response(response_data, 200, mimetype="application/json")

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/<section>", methods=["GET"]
)
def get_affiliation_section(affiliation_type: str, affiliation_id: str, section: str):
    if section == "affiliations":
        try:
            related_affiliations = (
                new_affiliation_service.get_related_affiliations_by_affiliation(
                    affiliation_id, affiliation_type
                )
            )

            return Response(
                json.dumps(related_affiliations), 200, mimetype="application/json"
            )

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
def get_affiliation(
    affiliation_id: str | None,
    affiliation_type: str | None = None,
    section: str | None = "info",
    tab: str | None = "products",
):
    try:
        params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify(str(e), 400)

    if section == "research" and tab == "products":
        if plot_type := request.args.get("plot"):
            return new_affiliation_service.get_affiliation_plot(
                affiliation_id, affiliation_type, plot_type, request.args
            )

        return affiliation_service.get_research_products(
            id=affiliation_id, typ=affiliation_type, params=params
        )


@affiliation_app_router.route(
    "/<affiliation_type>/<affiliation_id>/csv", methods=["GET"]
)
def get_csv_by_affiliation(affiliation_type: str, affiliation_id: str):
    try:
        data = new_affiliation_service.get_works_by_affiliation_csv(
            affiliation_id, affiliation_type
        )
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
