import json
from typing import Any
import io
import csv

from flask import Blueprint, request, Response, Request

from services.v1.affiliation_app import affiliation_app_service
from utils.encoder import JsonEncoder
from utils.flatten_json import flatten_json_list

router = Blueprint("affiliation_app_v1", __name__)


def affiliation(request: Request) -> dict[str, Any] | None:
    section = request.args.get("section")
    tab = request.args.get("tab")
    data = request.args.get("data")
    idx = request.args.get("id")
    typ = request.args.get("type")

    result = None

    if section == "info":
        result = affiliation_app_service.get_info(idx)
    elif section == "affiliations":
        result = affiliation_app_service.get_affiliations(idx, typ=typ)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                level = request.args.get("level", 0)
                args = (idx, typ, level) if plot == "products_subject" else (idx, typ)
                result = affiliation_app_service.plot_mappings[plot](*args)
            else:
                idx = request.args.get("id")
                typ = request.args.get("type")
                start_year = request.args.get("start_year")
                end_year = request.args.get("end_year")
                page = request.args.get("page")
                max_results = request.args.get("max_results")
                sort = request.args.get("sort")
                result = affiliation_app_service.get_research_products(
                    idx=idx,
                    typ=typ,
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
def get_affiliation():
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


@router.route("/csv", methods=["GET"])
def get_affiliation_csv():
    result = affiliation(request)
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

    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
