from flask import Flask
from flask_cors import CORS
from .config import configuration
from .utils.logger import setup_logging
import os

def create_app(config_class=None):
    app = Flask(__name__)
    
    app.config.from_object(config_class or configuration)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    setup_logging(app)
    
    ensure_directories(app)
    
    register_blueprints(app)
    
    register_error_handlers(app)
    
    app.logger.info("Application initialized successfully")
    app.logger.info(f"Environment: {'Development' if app.config['DEBUG'] else 'Production'}")
    app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    app.logger.info(f"GIF output folder: {app.config['GIF_OUTPUT_DIR']}")
    
    return app

def ensure_directories(app):
    """Create required directories if they don't exist"""
    for directory in [
        app.config['UPLOAD_FOLDER'],
        app.config['GIF_OUTPUT_DIR'],
        os.path.join(app.root_path, 'logs')
    ]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            app.logger.info(f"Created directory: {directory}")

def register_blueprints(app):
    """Register application blueprints"""
    from .routes.gif_routes import bp as gif_bp
    from .routes.utility_routes import bp as util_bp
    
    app.register_blueprint(gif_bp) 
    app.register_blueprint(util_bp) 
    
    app.logger.info("Registered API blueprints")

def register_error_handlers(app):
    """Register custom error handlers"""
    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    app.logger.info("Registered error handlers")