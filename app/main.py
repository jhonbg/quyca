from flask import Flask
from flask_cors import CORS

from api.router import api_router
from core.config import settings
from core.debugger import initialize_server_debugger_if_needed


app = Flask(__name__)
CORS(app)

app.register_blueprint(api_router)

if __name__ == "__main__":
    initialize_server_debugger_if_needed()
    app.run(host="0.0.0.0", port=8010, threaded=True, debug=True)
