from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas import (
    PersonQueryParams,
    AffiliationQueryParams,
    WorkQueryParams,
    SubjectQueryParams,
)
from services import person_service, affiliation_service, work_service, source_service

search_app_router = Blueprint("search_app_router", __name__)


@search_app_router.route("/person", methods=["GET"])
def read_person():
    try:
        query_params = PersonQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return person_service.search(params=query_params)


@search_app_router.route("/works", methods=["GET"])
def read_works():
    try:
        query_params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return work_service.search(params=query_params)


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
