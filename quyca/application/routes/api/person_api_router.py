from typing import Tuple

from flask import Blueprint, request, jsonify, Response

from domain.models.base_model import QueryParams
from domain.services import api_expert_service

person_api_router = Blueprint("person_api_router", __name__)


@person_api_router.route("/<person_id>/research/products", methods=["GET"])
def get_works_by_person_api_expert(person_id: str) -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        data = api_expert_service.get_works_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
