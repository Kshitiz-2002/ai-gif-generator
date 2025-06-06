from flask import Flask
from flask_cors import CORS
from .config import Config
from .utils.logger import setup_logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize logging
    setup_logging(app)
    
    # Register blueprints
    from app.routes import gif_routes, utility_routes
    app.register_blueprint(gif_routes.bp)
    app.register_blueprint(utility_routes.bp)
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app