from flask import Blueprint

from application.routes.api.apc_api_router import apc_api_router
from config import settings
from application.routes.app.other_work_app_router import other_work_app_router
from application.routes.app.patent_app_router import patent_app_router
from application.routes.app.project_app_router import project_app_router
from application.routes.app.search_app_router import search_app_router
from application.routes.api.search_api_router import search_api_router
from application.routes.app.affiliation_app_router import affiliation_app_router
from application.routes.api.affiliation_api_router import affiliation_api_router
from application.routes.app.person_app_router import person_app_router
from application.routes.api.person_api_router import person_api_router
from application.routes.app.work_app_router import work_app_router
from application.routes.docs_router import router as docs_router
from application.routes.ping_router import ping_router

router = Blueprint("router", __name__)

router.register_blueprint(ping_router)
router.register_blueprint(docs_router)

router.register_blueprint(search_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/search")
router.register_blueprint(search_api_router, url_prefix=f"{settings.API_URL_PREFIX}/search")

router.register_blueprint(affiliation_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/affiliation")
router.register_blueprint(affiliation_api_router, url_prefix=f"{settings.API_URL_PREFIX}/affiliation")

router.register_blueprint(person_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/person")
router.register_blueprint(person_api_router, url_prefix=f"{settings.API_URL_PREFIX}/person")

router.register_blueprint(work_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/work")

router.register_blueprint(other_work_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/other_work")

router.register_blueprint(patent_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/patent")

router.register_blueprint(project_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/project")

router.register_blueprint(apc_api_router, url_prefix=f"{settings.API_URL_PREFIX}/apc")
