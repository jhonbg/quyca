from flask import Blueprint

from api.routes.ping import router as ping_router
from core.config import settings
from api.routes.v2.search import router as search_router
from api.routes.v1.search_app import router as search_app_router_v1
from api.routes.v1.search_api import router as search_api_router_v1
from api.routes.v1.affiliation_app import router as affiliation_app_router_v1
from api.routes.v1.affiliation_api import router as affiliation_api_router_v1
from api.routes.v1.person_app import router as person_app_router_v1

api_router = Blueprint("router", __name__)

api_router.register_blueprint(ping_router)
api_router.register_blueprint(search_router, url_prefix=f"{settings.APP_V2_STR}")
api_router.register_blueprint(
    search_app_router_v1, url_prefix=f"{settings.APP_V1_STR}/search"
)
api_router.register_blueprint(
    search_api_router_v1, url_prefix=f"{settings.API_V1_STR}/search"
)
api_router.register_blueprint(
    affiliation_app_router_v1, url_prefix=f"{settings.APP_V1_STR}/affiliation"
)
api_router.register_blueprint(
    affiliation_api_router_v1, url_prefix=f"{settings.API_V1_STR}/affiliation"
)
api_router.register_blueprint(
    person_app_router_v1, url_prefix=f"{settings.APP_V1_STR}/person"
)
