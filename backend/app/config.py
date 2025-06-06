import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    GIF_OUTPUT_DIR = os.environ.get('GIF_OUTPUT_DIR', '/tmp/gifs')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
    
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')

    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 600))
    GIF_RESOLUTION = (
        int(os.environ.get('GIF_RESOLUTION_WIDTH', 640)),
        int(os.environ.get('GIF_RESOLUTION_HEIGHT', 360))
    )
    GIF_FPS = int(os.environ.get('GIF_FPS', 12))

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'