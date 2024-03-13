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
from utils.encoder import JsonEncoder

router = Blueprint("search_v1", __name__)


@router.route("/person", methods=["GET"])
def read_person():
    try:
        query_params = PersonQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_app_service.search_person(
        keywords=query_params.keywords,
        institutions=query_params.institutions,
        groups=query_params.groups,
        max_results=query_params.limit,
        page=query_params.page,
        sort=query_params.sort,
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="application/json",
    )


@router.route("/works", methods=["GET"])
def read_works():
    try:
        query_params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_app_service.search_work(
        keywords=query_params.keywords,
        max_results=query_params.limit,
        page=query_params.page,
        start_year=query_params.start_year,
        end_year=query_params.end_year,
        sort=query_params.sort,
        direction="descending",
        tipo=query_params.type,
        institutions=query_params.institutions,
        groups=query_params.groups,
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="application/json",
    )


@router.route("/affiliations/<type>", methods=["GET"])
def read_affiliations(type: str | None = None):
    try:
        query_params = AffiliationQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_app_service.search_affiliations(
        keywords=query_params.keywords,
        max_results=query_params.limit,
        page=query_params.page,
        sort=query_params.sort,
        aff_type=type,
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="application/json",
    )


@router.route("/subjects", methods=["GET"])
def read_subjects():
    try:
        query_params = SubjectQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_app_service.search_subjects(
        keywords=query_params.keywords,
        max_results=query_params.limit,
        page=query_params.page,
        sort=query_params.sort,
        direction="descending",
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="application/json",
    )