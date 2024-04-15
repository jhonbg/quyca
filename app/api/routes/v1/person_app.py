import json
import io
import csv

from flask import Blueprint, request, Response, Request

from services.v1.person_app import person_app_service
from utils.encoder import JsonEncoder
from utils.flatten_json import flatten_json_list

router = Blueprint("person_app_v1", __name__)


def person(
    request: Request, id: str | None, section: str | None = None, tab: str | None = None
):
    data = request.args.get("data")
    typ = request.args.get("typ", None)

    result = None

    if section == "info":
        result = person_app_service.get_info(id)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                level = request.args.get("level", 0)
                args = (id, level) if plot == "products_subject" else (id,)
                result = person_app_service.plot_mapping[plot](*args)
            else:
                typ = request.args.get("type")
                start_year = request.args.get("start_year")
                endt_year = request.args.get("end_year")
                page = request.args.get("page")
                max_results = request.args.get("max")
                sort = request.args.get("sort")
                result = person_app_service.get_research_products(
                    idx=id,
                    typ=typ,
                    start_year=start_year,
                    end_year=endt_year,
                    page=page,
                    max_results=max_results,
                    sort=sort,
                )
    else:
        result = None
    return result


@router.route("/<id>", methods=["GET"])
@router.route("/<id>/<section>/<tab>", methods=["GET"])
def get_person(
    id: str | None = None, section: str | None = "info", tab: str | None = None
):
    result = person(request, id=id, section=section, tab=tab)
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


@router.route("/<id>/csv", methods=["GET"])
@router.route("/<id>/<section>/<tab>/csv", methods=["GET"])
def get_person_csv(
    id: str | None = None, section: str | None = "info", tab: str | None = None
):
    if section == "research" and tab == "products":
        typ = request.args.get("type")
        start_year = request.args.get("start_year")
        endt_year = request.args.get("end_year")
        page = request.args.get("page")
        max_results = request.args.get("max")
        sort = request.args.get("sort")
        result = person_app_service.get_research_products_csv(
            idx=id,
            typ=typ,
            start_year=start_year,
            end_year=endt_year,
            page=page,
            max_results=max_results,
            sort=sort,
        )
    if result:
        config = {
            "authors": {"name": "author_names", "fields": ["full_name"]},
            "citations_count": {"name": "cited_by_count", "fields": ["count"]},
            # "subjects": {"name": "subjects", "fields": ["name"]},
            # "source": {"name": "source", "fields": ["name"]},
            "date_published": {
                "name": "date",
                "expresion": "datetime.date.fromtimestamp(value).strftime('%Y-%m-%d')",
            },
            "bibliographic_info": {
                "name": "biblio",
                "fields": [
                    "volume",
                    "issue",
                    "start_page",
                    "end_page",
                    # "is_open_access",
                    # "open_access_status",
                ],
            },
            "types": {"name": "type", "fields": ["type"]},
            "remove": ["abstract", "source", "references_count", "subtitle"],
            "titles": {
                "name": "title",
                "fields": ["title"],
                "expresion": "next(filter(lambda x: x['lang'] == 'es', list_data), list_data[0])['title']",
            },
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
        response.headers["Content-Disposition"] = "attachment; filename=person.csv"

    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )
    return response
