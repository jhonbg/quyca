from typing import Tuple

from flask import Blueprint, url_for, redirect, request, Response, jsonify
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from domain.services import api_expert_service

search_api_router = Blueprint("search_api_router", __name__)


@search_api_router.route("/person", methods=["GET"])
def search_persons() -> Response:
    return redirect(url_for("router.search_app_router.search_persons", **request.args))  # type: ignore


@search_api_router.route("/works", methods=["GET"])
def search_works() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = api_expert_service.search_works(query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@search_api_router.route("/affiliations", methods=["GET"])
def search_affiliations() -> Response:
    return redirect(url_for("router.search_app_router.search_affiliations", **request.args))  # type: ignore
