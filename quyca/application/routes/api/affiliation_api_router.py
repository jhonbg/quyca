from typing import Tuple

from flask import Blueprint, jsonify, request, Response
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from domain.services import api_expert_service

affiliation_api_router = Blueprint("affiliation_api_router", __name__)


@affiliation_api_router.route("/<affiliation_type>/<affiliation_id>/research/products", methods=["GET"])
def get_works_by_affiliation_api_expert(affiliation_id: str, affiliation_type: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = api_expert_service.get_works_by_affiliation(affiliation_id, query_params)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
