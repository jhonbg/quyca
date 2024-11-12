from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from domain.services import other_work_service

other_work_app_router = Blueprint("other_work_app_router", __name__)

"""
@api {get} /app/other_work/:other_work_id Get other work by id
@apiName GetOtherWorkById
@apiGroup Other Work
@apiVersion 1.0.0
@apiDescription Obtiene un producto de otro tipo por ID.

@apiParam {String} other_work_id ID del producto de otro tipo.
"""


@other_work_app_router.route("/<other_work_id>", methods=["GET"])
def get_other_work_by_id(other_work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = other_work_service.get_other_work_by_id(other_work_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/other_work/:other_work_id/authors Get other work authors
@apiName GetOtherWorkAuthors
@apiGroup Other Work
@apiVersion 1.0.0
@apiDescription Obtiene los autores de un producto de otro tipo.

@apiParam {String} other_work_id ID del producto de otro tipo.
"""


@other_work_app_router.route("/<other_work_id>/authors", methods=["GET"])
def get_other_work_authors(other_work_id: str) -> Response | Tuple[Response, int]:
    try:
        data = other_work_service.get_other_work_authors(other_work_id)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
