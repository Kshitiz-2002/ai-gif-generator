import os
import re
from flask import current_app
from werkzeug.utils import secure_filename
from .error_handlers import InvalidRequestError

ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "avi"}

def is_allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return ext in ALLOWED_EXTENSIONS

def validate_prompt(prompt: str):
    if not prompt or not prompt.strip():
        raise InvalidRequestError("Theme prompt cannot be empty.")
    if len(prompt.strip()) < 3:
        raise InvalidRequestError("Prompt must be at least 3 characters.")
    return prompt.strip()

def validate_youtube_url(url: str):
    pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/"
    if not re.match(pattern, url):
        raise InvalidRequestError("Invalid YouTube URL.")
    return url

def save_uploaded_file(file_storage):
    """Save an uploaded FileStorage to UPLOAD_FOLDER; return the saved file path."""
    if not file_storage:
        raise InvalidRequestError("No file provided.")
    filename = secure_filename(file_storage.filename)
    if not is_allowed_file(filename):
        raise InvalidRequestError(f"Unsupported file type: {filename}")
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    dst_path = os.path.join(upload_folder, filename)
    file_storage.save(dst_path)
    return dst_path