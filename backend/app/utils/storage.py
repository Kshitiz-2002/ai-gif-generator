import os
import uuid
from flask import current_app

def generate_unique_filename(original_filename: str):
    """Prepend a UUID to the secure filename to avoid collisions."""
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name

def ensure_directory(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def get_upload_folder() -> str:
    path = current_app.config["UPLOAD_FOLDER"]
    ensure_directory(path)
    return path

def get_gif_output_folder() -> str:
    path = current_app.config["GIF_OUTPUT_DIR"]
    ensure_directory(path)
    return path

def cleanup_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass