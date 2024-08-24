import os

from flask import Blueprint, send_from_directory, redirect, url_for

router = Blueprint("apidoc", __name__, static_folder=os.path.abspath("./quyca/core/docs/apidoc"))


@router.route("/apidoc/<path:path>")
def send_apidoc(path):
    return send_from_directory(router.static_folder, path)


@router.route('/apidoc')
def redirect_to_index():
    return redirect(url_for('router.apidoc.send_apidoc', path='index.html'))


@router.route('/docs')
def redirect_to_index_docs():
    return redirect(url_for('router.apidoc.send_apidoc', path='index.html'))