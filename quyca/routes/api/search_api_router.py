from flask import Blueprint, url_for, redirect, request, Response

search_api_router = Blueprint("search_api_router", __name__)


@search_api_router.route("/person", methods=["GET"])
def search_persons() -> Response:
    return redirect(url_for("router.search_app_router.search_persons", **request.args))  # type: ignore


@search_api_router.route("/works", methods=["GET"])
def search_works() -> Response:
    return redirect(url_for("router.search_app_router.search_works", **request.args))  # type: ignore


@search_api_router.route("/affiliations", methods=["GET"])
def search_affiliations() -> Response:
    return redirect(url_for("router.search_app_router.search_affiliations", **request.args))  # type: ignore
