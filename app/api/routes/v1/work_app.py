import json

from flask import Blueprint, request, Response

from services.v1.work_app import work_app_service
from utils.encoder import JsonEncoder

router = Blueprint("work_app_v1", __name__)


@router.route("/<id>", methods=["GET"])
def get_work(id: str | None):
    section = request.args.get("section")

    result = None

    if section == "info":
        result = work_app_service.get_info(id)

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
    return response