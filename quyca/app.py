import os

import sentry_sdk
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_compress import Compress
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from application.routes.router import router, limiter
from config import Settings


def create_app() -> Flask:
    app_settings = Settings()
    sentry_sdk.init(
        dsn=app_settings.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(project_dir, "application", "static")
    app_factory = Flask(__name__, static_folder=static_dir)

    app_factory.config["JWT_SECRET_KEY"] = app_settings.JWT_SECRET_KEY
    app_factory.config["JWT_ACCESS_TOKEN_EXPIRES"] = app_settings.JWT_ACCESS_TOKEN_EXPIRES

    JWTManager(app_factory)

    CORS(app_factory)
    app_factory.register_blueprint(router)
    Compress(app_factory)
    return app_factory


if __name__ == "__main__":
    settings = Settings()
    app = create_app()
    limiter.init_app(app)
    app.run(host="0.0.0.0", port=settings.APP_PORT, debug=settings.APP_DEBUG, threaded=True)
