from flask import Flask
from flask_cors import CORS

from quyca.api.router import api_router
from quyca.core.config import get_settings
from quyca.core.debugger import initialize_server_debugger_if_needed
from quyca.core.apidoc import generate_apidoc
from quyca.infraestructure.mongo import init_mongo_infraestructure


def create_app():
    app_factory = Flask(__name__)
    CORS(app_factory)
    app_factory.register_blueprint(api_router)

    return app_factory


if __name__ == "__main__":
    app = create_app()
    settings = get_settings()
    generate_apidoc()
    initialize_server_debugger_if_needed()
    init_mongo_infraestructure()

    app.run(
        host="0.0.0.0", port=settings.APP_PORT, threaded=True, debug=settings.APP_DEBUG
    )
