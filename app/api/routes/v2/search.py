from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas import PersonQueryParams, AffiliationQueryParams, WorkQueryParams
from services import person_service, affiliation_service, work_service

router = Blueprint("search", __name__)


@router.route("/search/person", methods=["GET"])
def read_person():
    try:
        query_params = PersonQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return person_service.search(params=query_params)


@router.route("/search/works", methods=["GET"])
def read_works():
    try:
        query_params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return work_service.search(params=query_params)


@router.route("/search/affiliations", methods=["GET"])
def read_affiliations():
    try:
        query_params = AffiliationQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return affiliation_service.search(params=query_params)
