import json
import io
import csv

from flask import Blueprint, request, Response, jsonify
from pydantic import ValidationError

from services.affiliation import affiliation_service
from schemas.work import WorkQueryParams
from utils.encoder import JsonEncoder
from utils.flatten_json import flatten_json_list

router = Blueprint("affiliation_app_v1", __name__)


@router.route("/<typ>/<id>", methods=["GET"])
@router.route("/<typ>/<id>/<section>", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>", methods=["GET"])
def get_affiliation(
    id: str | None,
    typ: str | None = None,
    section: str | None = "info",
    tab: str | None = "products",
):
    try:
        params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify(str(e), 400)
    if section == "info":
        return affiliation_service.get_info(id=id)
    if section == "affiliations":
        return affiliation_service.get_affiliations(id=id, typ=typ)
    if section == "research" and tab == "products":
        if plot := request.args.get("plot"):
            level = int(request.args.get("level", 0))
            _typ = plot.split(",")[-1] if "," in plot else typ
            args = (
                (id, level, _typ, typ) if plot == "products_subject" else (id, _typ, typ)
            )
            return affiliation_service.plot_mappings[plot](*args)
        return affiliation_service.get_research_products(id=id, typ=typ, params=params)


@router.route("/<typ>/<id>/csv", methods=["GET"])
@router.route("/<typ>/<id>/<section>/csv", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>/csv", methods=["GET"])
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
