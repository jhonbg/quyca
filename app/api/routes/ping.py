from flask import Blueprint

from core.config import settings

router = Blueprint("ping", __name__)

@router.route('/ping', methods=['GET'])
def read_root():
    """Ping the API."""
    result = {"ping": str(settings.MONGO_URI)}
    return result