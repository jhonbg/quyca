from flask import Blueprint, request, Response, jsonify

from database.models.base_model import QueryParams
from services import person_service, work_service, csv_service

person_app_router = Blueprint("person_app_router", __name__)


@person_app_router.route("/<person_id>", methods=["GET"])
def get_person_by_id(person_id: str):
    try:
        data = person_service.get_person_by_id(person_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/products", methods=["GET"])
def get_person_research_products(person_id: str):
    try:
        query_params = QueryParams(**request.args)
        if query_params.plot:
            data = person_service.get_person_plot(person_id, query_params)
            return jsonify(data)
        data = work_service.get_works_by_person(person_id, query_params)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@person_app_router.route("/<person_id>/research/products/csv", methods=["GET"])
def get_works_csv_by_person(person_id: str):
    try:
        data = csv_service.get_works_csv_by_person(person_id)
        response = Response(data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=affiliation.csv"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 400
