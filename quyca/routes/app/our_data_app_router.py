import json

from flask import Blueprint, Response

from services.v1.our_data_app import our_data_app_service
from utils.encoder import JsonEncoder

our_data_app_router = Blueprint("our_data_app_router", __name__)


@our_data_app_router.route("", methods=["GET"])
def get_our_data():
    result = our_data_app_service.get_our_data()
    if result:
        response = Response(
            response=json.dumps(result, cls=JsonEncoder),
            status=200,
            mimetype="application/json",
        )
    else:
        response = Response(
            response=json.dumps({}, cls=JsonEncoder),
            status=204,
            mimetype="application/json",
        )

    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
