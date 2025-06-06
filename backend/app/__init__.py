# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS
from .config import configuration
from .utils.logger import setup_logging

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or configuration)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    setup_logging(app)

    from .routes.gif_routes import bp as gif_bp
    from .routes.utility_routes import bp as util_bp
    app.register_blueprint(gif_bp, url_prefix="/api")
    app.register_blueprint(util_bp, url_prefix="/api")

    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
