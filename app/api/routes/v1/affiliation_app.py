import json
from typing import Any
import io
import csv

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_app import affiliation_app_service
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
                start_year = request.args.get("start_year")
                end_year = request.args.get("end_year")
                page = request.args.get("page")
                max_results = request.args.get("max")
                sort = request.args.get("sort")
                result = affiliation_app_service.get_research_products(
                    idx=idx,
                    typ=aff_type,
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
def get_affiliation_csv(id: str | None, typ: str | None = None):
    result = affiliation(request, idx=id, typ=typ)
    if result:
        config = {
            "authors": ["full_name"],
            "citations_count": ["source", "count"],
            "subjects": ["name"],
        }
        flat_data_list = flatten_json_list(result["data"], config, 1)
        all_keys = set()
        for item in flat_data_list:
            all_keys.update(item.keys())

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
