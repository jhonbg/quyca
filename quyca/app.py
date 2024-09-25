import sentry_sdk
from flask import Flask
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from application.routes.router import router
from config import Settings


def create_app() -> Flask:
    app_factory = Flask(__name__)
    app_settings = Settings()
    sentry_sdk.init(
        dsn=app_settings.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    CORS(app_factory)
    app_factory.register_blueprint(router)
    return app_factory


if __name__ == "__main__":
    settings = Settings()
    app = create_app()
    app.run(host="0.0.0.0", port=settings.APP_PORT, debug=settings.APP_DEBUG, threaded=True)
