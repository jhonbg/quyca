import json

from flask import Blueprint, request, jsonify, Response
from pydantic import ValidationError

from schemas import (
    PersonQueryParams,
    AffiliationQueryParams,
    WorkQueryParams,
    SubjectQueryParams,
)
from services.v1.search_api import search_api_service
from services import work_service
from utils.encoder import JsonEncoder

search_api_router = Blueprint("search_api_router", __name__)


@search_api_router.route("/person", methods=["GET"])
def read_person():
    """
    @api {get} /search/person search by person name
    @apiVersion 1.0.0
    @apiName get_search_person
    @apiGroup Search

    @apiQuery {String}    [keywords]        The keywords to search.
    @apiQuery {Number}    [page=1]          Number of page.
    @apiQuery {Number{1-250}}    [max=10]          Number of results per page.
    # @apiQuery {String}    [sort=alphabetical]          Sort by field.

    """
    try:
        query_params = PersonQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_api_service.search_person(
        keywords=query_params.keywords,
        institutions=query_params.institutions,
        groups=query_params.groups,
        max_results=query_params.max,
        page=query_params.page,
        sort=query_params.sort,
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="apilication/json",
    )


@search_api_router.route("/works", methods=["GET"])
def read_works():
    """
    @api {get} /search/works search by work title
    @apiVersion 1.0.0
    @apiName get_search_works
    @apiGroup Search

    @apiQuery {String}    [keywords]        The keywords to search.
    @apiQuery {Number}    [page=1]          Number of page.
    @apiQuery {Number{1-250}}    [max=10]          Number of results per page.
    # @apiQuery {String="alphabetical","citations"}    [sort=alphabetical]          Sort by field.

    """
    try:
        query_params = WorkQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    return work_service.search_api(params=query_params)


@search_api_router.route("/affiliations", methods=["GET"])
def read_affiliations():
    """
    @api {get} /search/affiliations search by affiliation name
    @apiVersion 1.0.0
    @apiName get_search_affiliations
    @apiGroup Search

    @apiQuery {String}    [keywords]        The keywords to search.
    @apiQuery {Number}    [page=1]          Number of page.
    @apiQuery {Number{1-250}}    [max=10]          Number of results per page.
    # @apiQuery {String}    [sort=alphabetical]          Sort by field.

    """
    try:
        query_params = AffiliationQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_api_service.search_affiliations(
        keywords=query_params.keywords,
        max_results=query_params.max,
        page=query_params.page,
        sort=query_params.sort,
        aff_type=query_params.type,
    )
    return Response(
        response=json.dumps(
            results,
            cls=JsonEncoder,
        ),
        status=200,
        mimetype="apilication/json",
    )


@search_api_router.route("/subjects", methods=["GET"])
def read_subjects():
    """
    @api {get} /search/subjects search by subject
    @apiVersion 1.0.0
    @apiName get_search_subjects
    @apiGroup Search

    @apiQuery {String}    [keywords]        The keywords to search.
    @apiQuery {Number}    [page=1]          Number of page.
    @apiQuery {Number{1-250}}    [max=10]          Number of results per page.
    # @apiQuery {String}    [sort=alphabetical]          Sort by field.


    """
    try:
        query_params = SubjectQueryParams(**request.args)
    except ValidationError as e:
        return jsonify({"error": str(e)}, 400)
    results = search_api_service.search_subjects(
        keywords=query_params.keywords,
        max_results=query_params.max,
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
        mimetype="apilication/json",
    )
