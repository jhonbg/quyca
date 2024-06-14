import json
from typing import Any
import io
import csv

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_app import affiliation_app_service
from services.work import work_service
from schemas.work import WorkQueryParams
from utils.encoder import JsonEncoder
from utils.flatten_json import flatten_json_list

router = Blueprint("affiliation_app_v1", __name__)


def affiliation(
    request: Request,
    *,
    idx: str | None = None,
    aff_type: str | None = None,
    section: str | None = None,
    tab: str | None = None,
) -> dict[str, Any] | None:
    result = None
    if section == "info":
        result = affiliation_app_service.get_info(idx, aff_type)
    elif section == "affiliations":
        result = affiliation_app_service.get_affiliations(idx, typ=aff_type)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                level = int(request.args.get("level", 0))
                typ = plot.split(",")[-1] if "," in plot else aff_type
                args = (
                    (idx, level, typ, aff_type)
                    if plot == "products_subject"
                    else (idx, typ, aff_type)
                )
                result = affiliation_app_service.plot_mappings[plot](*args)
            else:
                params = WorkQueryParams(**request.args)
                result = work_service.get_research_products_by_affiliation(
                    affiliation_id=idx,
                    affiliation_type=aff_type,
                    skip=params.skip,
                    limit=params.max,
                    sort=params.sort,
                    filters=params.get_filter(),
                )
    else:
        result = None
    return result


@router.route("/<typ>/<id>", methods=["GET"])
@router.route("/<typ>/<id>/<section>", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>", methods=["GET"])
def get_affiliation(
    id: str | None,
    typ: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
):
    result = affiliation(request, idx=id, aff_type=typ, section=section, tab=tab)
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


@router.route("/<typ>/<id>/csv", methods=["GET"])
@router.route("/<typ>/<id>/<section>/csv", methods=["GET"])
@router.route("/<typ>/<id>/<section>/<tab>/csv", methods=["GET"])
def get_affiliation_csv(
    id: str | None,
    typ: str | None = None,
    section: str | None = "info",
    tab: str | None = None,
):
    result = work_service.get_research_products_info_by_affiliation_csv(
        affiliation_id=id, affiliation_type=typ
    )
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
            "subject_names": {
                "name": "temas"
            },
            "doi": {
                "name": "doi"
            },
            "source_name": {
                "name": "revista"
            }
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
