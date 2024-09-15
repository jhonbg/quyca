from flask import Blueprint, url_for, redirect, request

search_api_router = Blueprint("search_api_router", __name__)


@search_api_router.route("/person", methods=["GET"])
def search_persons():
    return redirect(url_for("router.search_app_router.search_persons", **request.args))


@search_api_router.route("/works", methods=["GET"])
def search_works():
    return redirect(url_for("router.search_app_router.search_works", **request.args))


@search_api_router.route("/affiliations", methods=["GET"])
def search_affiliations():
    return redirect(url_for("router.search_app_router.search_affiliations", **request.args))
