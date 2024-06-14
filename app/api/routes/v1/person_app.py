import json
import io
import csv

from flask import Blueprint, request, Response, Request

# from flask_apidoc import ApiDoc

from services.v1.person_app import person_app_service
from services.person import person_service
from services.work import work_service
from schemas.work import WorkQueryParams
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
        result = person_service.get_info(id=id)
    elif section == "research":
        if tab == "products":
            plot = request.args.get("plot")
            if plot:
                level = request.args.get("level", 0)
                args = (id, level) if plot == "products_subject" else (id,)
                result = person_app_service.plot_mapping[plot](*args)
            else:
                params = WorkQueryParams(**request.args)
                result = work_service.get_research_products_by_author(
                    author_id=id,
                    skip=params.skip,
                    limit=params.max,
                    sort=params.sort,
                    filters=params.get_filter(),
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
    result = work_service.get_research_products_by_author_csv(author_id=id)
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
            "subjects": {
                "name": "temas",
                "fields": ["name"],
                "config": {"name": {"name": "name"}},
            },
            "doi": {"name": "doi"},
            "source_name": {"name": "revista"},
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
        response.headers["Content-Disposition"] = "attachment; filename=person.csv"

    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )
    return response
