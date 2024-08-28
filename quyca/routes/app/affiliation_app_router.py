import json
import io
import csv

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
        response_data = json.dumps({"data": affiliation.model_dump(by_alias=True), "filters": {}})

        return Response(response_data, 200, mimetype="application/json")

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/<section>", methods=["GET"])
def get_affiliation_section(affiliation_type: str, affiliation_id: str, section: str):
    if section == "affiliations":
        try:
            related_affiliations = new_affiliation_service.get_related_affiliations_by_affiliation(
                affiliation_id, affiliation_type
            )

            return Response(json.dumps(related_affiliations), 200, mimetype = "application/json")

        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")

    return Response(json.dumps({"error": f"There is no {section} section"}), 400, mimetype="application/json")


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/<section>/<tab>", methods=["GET"])
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
            return new_affiliation_service.get_affiliation_plot(affiliation_id, affiliation_type, plot_type, request.args)

        return affiliation_service.get_research_products(id=affiliation_id, typ=affiliation_type, params=params)


@affiliation_app_router.route("/<affiliation_type>/<affiliation_id>/csv", methods=["GET"])
def get_csv_by_affiliation(affiliation_type: str, affiliation_id: str):
    try:
        data = new_affiliation_service.get_works_by_affiliation_csv(affiliation_id, affiliation_type)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@affiliation_app_router.route("/<typ>/<id>/<section>/csv", methods=["GET"])
@affiliation_app_router.route("/<typ>/<id>/<section>/<tab>/csv", methods=["GET"])
def get_affiliation_csv(
    id: str | None,
    typ: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
):
    result = affiliation_service.get_research_products_csv(id=id, typ=typ)
    if result:
        config = {
            "title": {
                "name": "titulo",
            },
            "authors": {
                "name": "autores",
                "fields": ["full_name"],
                "config": {"full_name": {"name": "full_name"}},
            },
            "lenguage": {"name": "lengua"},
            "citations_count": {
                "name": "veces citado",
                "fields": ["count"],
                "config": {"count": {"name": "count"}},
            },
            "date_published": {
                "name": "fecha publicación",
                "expresion": "datetime.date.fromtimestamp(value).strftime('%Y-%m-%d')",
            },
            "volume": {"name": "volumen"},
            "issue": {"name": "issue"},
            "start_page": {"name": "página inicial"},
            "end_page": {"name": "página final"},
            "year_published": {"name": "año de publicación"},
            "types": {"name": "tipo de producto", "fields": ["type"]},
            "subject_names": {"name": "temas"},
            "doi": {"name": "doi"},
            "source_name": {"name": "revista"},
            "scimago_quartile": {"name": "cuartil de scimago"},
        }
        flat_data_list = flatten_json_list(result, config, 1)
        all_keys = []
        for item in flat_data_list:
            all_keys += [key for key in item.keys() if key not in all_keys]

        output = io.StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=all_keys)
        csv_writer.writeheader()
        csv_writer.writerows(flat_data_list)

        response = Response(output.getvalue(), content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"

    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )

    return response
