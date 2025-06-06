import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    GIF_OUTPUT_DIR = os.getenv('GIF_OUTPUT_DIR', '/tmp/gifs')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', 600))
    GIF_RESOLUTION = (
        int(os.getenv('GIF_RESOLUTION_WIDTH', 640)),
        int(os.getenv('GIF_RESOLUTION_HEIGHT', 360))
    )
    GIF_FPS = int(os.getenv('GIF_FPS', 12))
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


configuration = Config()