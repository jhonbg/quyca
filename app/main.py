from flask import Flask
from flask_cors import CORS

from api.router import api_router
from core.config import settings
from core.debugger import initialize_server_debugger_if_needed
from core.apidoc import generate_apidoc
from infraestructure.mongo import init_mongo_infraestructure

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_router)

if __name__ == "__main__":
    generate_apidoc()

    initialize_server_debugger_if_needed()

    init_mongo_infraestructure()

    app.run(
        host="0.0.0.0", port=settings.APP_PORT, threaded=True, debug=settings.APP_DEBUG
    )
