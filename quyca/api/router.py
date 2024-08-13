from flask import Blueprint

from api.routes.ping import router as ping_router
from core.config import settings
from api.routes.views.search import router as search_app_router_v1
from api.routes.json.search import router as search_api_router_v1
from api.routes.views.affiliation import router as affiliation_app_router_v1
from api.routes.json.affiliation import router as affiliation_api_router_v1
from api.routes.views.person import router as person_app_router_v1
from api.routes.json.person import router as person_api_router_v1
from api.routes.views.work import router as work_app_router_v1
from api.apidoc import router as apidoc_router

api_router = Blueprint("router", __name__)

api_router.register_blueprint(ping_router)

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
api_router.register_blueprint(
    person_api_router_v1, url_prefix=f"{settings.API_V1_STR}/person"
)

api_router.register_blueprint(
    work_app_router_v1, url_prefix=f"{settings.APP_V1_STR}/work"
)
api_router.register_blueprint(apidoc_router, url_prefix="")
