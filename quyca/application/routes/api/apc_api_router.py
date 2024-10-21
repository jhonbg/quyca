from typing import Tuple

from bson import ObjectId
from flask import Blueprint, request, jsonify, Response
from sentry_sdk import capture_exception

from domain.models.base_model import QueryParams
from infrastructure.mongo import database

apc_api_router = Blueprint("apc_api_router", __name__)


@apc_api_router.route("/search", methods=["GET"])
def apc_search() -> Response | Tuple[Response, int]:
    try:
        query_params = QueryParams(**request.args)
        pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
        pipeline += [
            {
                "$lookup": {
                    "from": "sources",  # type: ignore
                    "localField": "source.id",  # type: ignore
                    "foreignField": "_id",  # type: ignore
                    "as": "source_data",  # type: ignore
                    "pipeline": [  # type: ignore
                        {"$project": {"_id": 0, "apc": 1}},
                    ],
                }
            },
            {"$unwind": "$source_data"},  # type: ignore
            {
                "$project": {
                    "_id": 0,  # type: ignore
                    "doi": 1,  # type: ignore
                    "source_apc_value": "$source_data.apc.charges",  # type: ignore
                    "source_apc_currency": "$source_data.apc.currency",  # type: ignore
                    "work_apc_currency": "$apc.paid.currency",  # type: ignore
                    "work_apc_value": "$apc.paid.value",  # type: ignore
                }
            },
        ]
        data = database["works"].aggregate(pipeline)
        return jsonify(list(data))
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/person/<person_id>", methods=["GET"])
def apc_person(person_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline = [
            {"$match": {"authors.id": ObjectId(person_id)}},
            {
                "$lookup": {
                    "from": "sources",  # type: ignore
                    "localField": "source.id",  # type: ignore
                    "foreignField": "_id",  # type: ignore
                    "as": "source_data",  # type: ignore
                    "pipeline": [  # type: ignore
                        {"$project": {"_id": 0, "apc": 1}},
                    ],  # type: ignore
                }
            },
            {"$unwind": "$source_data"},  # type: ignore
            {
                "$project": {
                    "_id": 0,
                    "doi": 1,
                    "source_apc_value": "$source_data.apc.charges",
                    "source_apc_currency": "$source_data.apc.currency",
                    "work_apc_currency": "$apc.paid.currency",
                    "work_apc_value": "$apc.paid.value",
                }
            },
        ]
        data = database["works"].aggregate(pipeline)
        return jsonify(list(data))
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


@apc_api_router.route("/affiliation/<affiliation_id>", methods=["GET"])
def apc_affiliation(affiliation_id: str) -> Response | Tuple[Response, int]:
    try:
        pipeline = [
            {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
            {
                "$lookup": {
                    "from": "sources",  # type: ignore
                    "localField": "source.id",  # type: ignore
                    "foreignField": "_id",  # type: ignore
                    "as": "source_data",  # type: ignore
                    "pipeline": [  # type: ignore
                        {"$project": {"_id": 0, "apc": 1}},
                    ],  # type: ignore
                }
            },
            {"$unwind": "$source_data"},  # type: ignore
            {
                "$project": {
                    "_id": 0,
                    "doi": 1,
                    "source_apc_value": "$source_data.apc.charges",
                    "source_apc_currency": "$source_data.apc.currency",
                    "work_apc_currency": "$apc.paid.currency",
                    "work_apc_value": "$apc.paid.value",
                }
            },
        ]
        data = database["works"].aggregate(pipeline)
        return jsonify(list(data))
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
