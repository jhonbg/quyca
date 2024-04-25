import json

from flask import Blueprint, request, jsonify, Response
from pydantic import ValidationError

from schemas import (
    PersonQueryParams,
    AffiliationQueryParams,
    WorkQueryParams,
    SubjectQueryParams,
)
from services.v1.search_app import search_app_service
from services import person_service, affiliation_service, work_service, source_service
from utils.encoder import JsonEncoder

router = Blueprint("search_v1", __name__)


@router.route("/person", methods=["GET"])
def read_person():
    try:
        query_params = PersonQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return person_service.search(params=query_params)


@router.route("/works", methods=["GET"])
def read_works():
    try:
        query_params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return work_service.search(params=query_params)


@router.route("/affiliations/<type>", methods=["GET"])
def read_affiliations(type: str | None = None):
    try:
        query_params = AffiliationQueryParams(**request.args, type=type)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return affiliation_service.search(params=query_params)


@router.route("/subjects", methods=["GET"])
def read_subjects():
    try:
        query_params = SubjectQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return source_service.search(params=query_params)