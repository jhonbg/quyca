from flask import Blueprint

from application.routes.api.apc_api_router import apc_api_router
from application.routes.app.info_app_router import info_app_router
from config import settings
from application.routes.app.patent_app_router import patent_app_router
from application.routes.app.project_app_router import project_app_router
from application.routes.app.search_app_router import search_app_router
from application.routes.api.search_api_router import search_api_router
from application.routes.app.affiliation_app_router import affiliation_app_router
from application.routes.api.affiliation_api_router import affiliation_api_router
from application.routes.app.user_auth_app_router import user_auth_app_router
from application.routes.app.staff_app_router import staff_app_router
from application.routes.app.ciarp_app_router import ciarp_app_router
from application.routes.app.person_app_router import person_app_router
from application.routes.api.person_api_router import person_api_router
from application.routes.app.work_app_router import work_app_router
from application.routes.docs_router import router as docs_router
from application.routes.ping_router import ping_router

from application.routes.app.completer_app_router import completer_app_router

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import settings

limiter = Limiter(get_remote_address, storage_uri=str(settings.MONGO_URI), strategy="fixed-window")

for limit in settings.API_LIMITS.split(","):
    limiter.limit(limit)(person_api_router)
    limiter.limit(limit)(search_api_router)
    limiter.limit(limit)(affiliation_api_router)
    limiter.limit(limit)(apc_api_router)
    limiter.limit(limit)(ping_router)
    limiter.limit(limit)(docs_router)

router = Blueprint("router", __name__)

router.register_blueprint(ping_router)
router.register_blueprint(docs_router)

router.register_blueprint(info_app_router, url_prefix=f"{settings.APP_URL_PREFIX}")

router.register_blueprint(search_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/search")
router.register_blueprint(search_api_router, url_prefix=f"{settings.API_URL_PREFIX}/search")

router.register_blueprint(affiliation_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/affiliation")
router.register_blueprint(affiliation_api_router, url_prefix=f"{settings.API_URL_PREFIX}/affiliation")

router.register_blueprint(person_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/person")
router.register_blueprint(person_api_router, url_prefix=f"{settings.API_URL_PREFIX}/person")

router.register_blueprint(work_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/work")

router.register_blueprint(patent_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/patent")

router.register_blueprint(project_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/project")

router.register_blueprint(apc_api_router, url_prefix=f"{settings.API_URL_PREFIX}/apc")

router.register_blueprint(completer_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/completer")

router.register_blueprint(user_auth_app_router, url_prefix=f"{settings.APP_URL_PREFIX}")

router.register_blueprint(staff_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/submit")

router.register_blueprint(ciarp_app_router, url_prefix=f"{settings.APP_URL_PREFIX}/submit")
