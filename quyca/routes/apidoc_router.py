from flask import Blueprint, redirect

router = Blueprint("apidoc", __name__)


@router.route("/apidoc")
def redirect_to_index():
    return redirect("static/index.html")


@router.route("/docs")
def redirect_to_index_docs():
    return redirect("static/index.html")
