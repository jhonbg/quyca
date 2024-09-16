from flask import Blueprint, redirect
from werkzeug import Response

router = Blueprint("apidoc", __name__)


@router.route("/apidoc")
def redirect_to_index() -> Response:
    return redirect("static/index.html")


@router.route("/docs")
def redirect_to_index_docs() -> Response:
    return redirect("static/index.html")
