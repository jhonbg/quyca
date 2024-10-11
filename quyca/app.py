import os

from flask import Flask
from flask_cors import CORS

from application.routes.router import router
from config import Settings


def create_app() -> Flask:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(project_dir, "application", "static")
    app_factory = Flask(__name__, static_folder=static_dir)
    CORS(app_factory)
    app_factory.register_blueprint(router)
    return app_factory


if __name__ == "__main__":
    settings = Settings()
    app = create_app()
    app.run(host="0.0.0.0", port=settings.APP_PORT, debug=settings.APP_DEBUG, threaded=True)
