from flask import Blueprint, redirect
from werkzeug import Response

router = Blueprint("apidoc", __name__)


@router.route("/apidoc")
def redirect_to_index() -> Response:
    return redirect("static/index.html")


@router.route("/docs")
def redirect_to_index_docs() -> Response:
    return redirect("static/index.html")


@router.route("/robots.txt")
def redirect_to_robots() -> Response:
    return redirect("static/robots.txt")


@router.route("/google54c758d287263571.html")
def redirect_to_google() -> Response:
    return redirect("static/google54c758d287263571.html")
