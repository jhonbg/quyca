import json

from flask import Blueprint, request, jsonify, Response
from pydantic import ValidationError

from database.models.base_model import QueryParams
from schemas import (
    AffiliationQueryParams,
    WorkQueryParams,
    SubjectQueryParams,
)
from services import (
    affiliation_service,
    work_service,
    source_service,
    new_person_service,
    new_work_service,
)

search_app_router = Blueprint("search_app_router", __name__)


@search_app_router.route("/person", methods=["GET"])
def search_persons():
    try:
        query_params = QueryParams(**request.args)
        data = new_person_service.search_persons(query_params)
        return Response(json.dumps(data), 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@search_app_router.route("/works", methods=["GET"])
def search_works():
    try:
        query_params = QueryParams(**request.args)
        data = new_work_service.search_works(query_params)
        return Response(json.dumps(data), 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@search_app_router.route("/affiliations/<affiliation_type>", methods=["GET"])
def read_affiliations(affiliation_type: str | None = None):
    try:
        query_params = AffiliationQueryParams(**request.args, type=affiliation_type)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)

    return affiliation_service.search(params=query_params)


@search_app_router.route("/subjects", methods=["GET"])
def read_subjects():
    try:
        query_params = SubjectQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return source_service.search(params=query_params)
