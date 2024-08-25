import os

from flask import Blueprint, send_from_directory, redirect, url_for

router = Blueprint("apidoc", __name__)


@router.route('/apidoc')
def redirect_to_index():
    return redirect("static/index.html")


@router.route('/docs')
def redirect_to_index_docs():
    return redirect("static/index.html")