from flask import Blueprint

from core.config import settings
from routes.app.search_app_router import search_app_router
from routes.api.search_api_router import search_api_router
from routes.app.affiliation_app_router import affiliation_app_router
from routes.api.affiliation_api_router import affiliation_api_router
from routes.app.person_app_router import person_app_router
from routes.api.person_api_router import person_api_router
from routes.app.work_app_router import work_app_router
from routes.apidoc_router import router as apidoc_router
from routes.ping_router import ping_router

router = Blueprint("router", __name__)

router.register_blueprint(ping_router)
router.register_blueprint(apidoc_router)

router.register_blueprint(search_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/search")
router.register_blueprint(search_api_router, url_prefix=f"{settings.API_URL_PREFIX}/search")

router.register_blueprint(affiliation_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/affiliation")
router.register_blueprint(affiliation_api_router, url_prefix=f"{settings.API_URL_PREFIX}/affiliation")

router.register_blueprint(person_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/person")
router.register_blueprint(person_api_router, url_prefix=f"{settings.API_URL_PREFIX}/person")

router.register_blueprint(work_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/work")
