from flask import Blueprint, jsonify, current_app
import logging

import os
import shutil
from app.config import configuration

logger = logging.getLogger(__name__)

bp = Blueprint('utility', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "message": "GIF generator service is running",
        "version": "1.0.0"
    })


@bp.route('/config', methods=['GET'])
def show_config():
    """
    Show current configuration
    """
    from app.config import configuration
    return jsonify({
        "max_video_duration": configuration.MAX_VIDEO_DURATION,
        "gif_resolution": configuration.GIF_RESOLUTION,
        "gif_fps": configuration.GIF_FPS,
        "whisper_model": configuration.WHISPER_MODEL,
        "max_gif_duration": configuration.MAX_GIF_DURATION,
    })


@bp.route('/cleanup', methods=['POST'])
def cleanup_temp_files():
    """
    Cleanup temporary files (admin endpoint)
    """    
    try:
        # Clean uploads
        if os.path.exists(configuration.UPLOAD_FOLDER):
            shutil.rmtree(configuration.UPLOAD_FOLDER)
            os.makedirs(configuration.UPLOAD_FOLDER)
        
        # Clean GIF outputs
        if os.path.exists(configuration.GIF_OUTPUT_DIR):
            shutil.rmtree(configuration.GIF_OUTPUT_DIR)
            os.makedirs(configuration.GIF_OUTPUT_DIR)
        
        return jsonify({
            "status": "success",
            "message": "Temporary files cleaned"
        })
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    