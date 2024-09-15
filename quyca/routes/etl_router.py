import json

from flask import Blueprint, Response

from services import etl_service

etl_router = Blueprint("etl_router", __name__)


@etl_router.route("/set_person_products_count", methods=["GET"])
def set_person_products_count():
    try:
        etl_service.set_person_products_count()
        return Response(json.dumps("The etl is done"), 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")


@etl_router.route("/set_person_citations_count", methods=["GET"])
def set_person_citations_count():
    try:
        etl_service.set_person_citations_count()
        return Response(json.dumps("The etl is done"), 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
