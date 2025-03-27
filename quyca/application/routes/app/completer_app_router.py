from typing import Tuple

from flask import Blueprint, jsonify, Response
from sentry_sdk import capture_exception

from infrastructure.repositories import completers

completer_app_router = Blueprint("completer_app_router", __name__)

"""
@api {get} /app/completer/person/:text Get completion suggestions
@apiName GetPersonCompleter
@apiGroup Completer
@apiVersion 1.0.0
@apiDescription Allows to get completion options for person.

@apiParam {String} text with the name of the author.
"""


@completer_app_router.route("/person/<text>", methods=["GET"])
def get_person_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.person_completer(text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
