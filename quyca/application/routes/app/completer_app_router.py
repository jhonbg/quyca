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


"""
@api {get} /app/completer/affiliations/institution/:text Get completion suggestions
@apiName GetInstitutionCompleter
@apiGroup Completer
@apiVersion 1.0.0
@apiDescription Allows to get completion options for institutions.

@apiParam {String} text with the name of the institutions.
"""


@completer_app_router.route("/affiliations/institution/<text>", methods=["GET"])
def get_institution_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("institution", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/completer/affiliations/group/:text Get completion suggestions
@apiName GetGroupCompleter
@apiGroup Completer
@apiVersion 1.0.0
@apiDescription Allows to get completion options for research groups.

@apiParam {String} text with the name of the groups.
"""


@completer_app_router.route("/affiliations/group/<text>", methods=["GET"])
def get_group_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("group", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/completer/affiliations/department/:text Get completion suggestions
@apiName GetDepartmentCompleter
@apiGroup Completer
@apiVersion 1.0.0
@apiDescription Allows to get completion options for academic departments.

@apiParam {String} text with the name of the departments.
"""


@completer_app_router.route("/affiliations/department/<text>", methods=["GET"])
def get_department_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("department", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400


"""
@api {get} /app/completer/affiliations/faculty/:text Get completion suggestions
@apiName GetFacultyCompleter
@apiGroup Completer
@apiVersion 1.0.0
@apiDescription Allows to get completion options for academic faculties.

@apiParam {String} text with the name of the faculties.
"""


@completer_app_router.route("/affiliations/faculty/<text>", methods=["GET"])
def get_faculty_completion(text: str) -> Response | Tuple[Response, int]:
    try:
        data = completers.affiliations_completer("faculty", text)
        return jsonify(data)
    except Exception as e:
        capture_exception(e)
        return jsonify({"error": str(e)}), 400
