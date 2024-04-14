from flask import Blueprint

router = Blueprint("info_v1", __name__)

@router.route("/info", methods=["GET"])
def get_info():
    return {"info": "This is the info endpoint!"}