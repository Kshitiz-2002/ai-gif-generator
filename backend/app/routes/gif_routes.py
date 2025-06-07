import os
import uuid
import logging
import tempfile
import shutil
from flask import Flask, Blueprint, request, jsonify, send_file, current_app
from app.core import video_processor, transcription, caption_selector, gif_generator
from app.utils import storage, validation
from app.utils.error_handlers import InvalidRequestError, VideoProcessingError

logger = logging.getLogger(__name__)

bp = Blueprint("gif", __name__, url_prefix="/api/gif")

@bp.route("/generate", methods=["POST"])
def generate_gif():
    """
    Generate GIFs from video based on theme prompt.
    Supports YouTube URLs or file uploads.
    Returns a list of GIF URLs with metadata.
    """
    prompt = request.form.get("prompt", "").strip()
    youtube_url = request.form.get("youtube_url", "").strip()
    video_file = request.files.get("video")

    try:
        prompt = validation.validate_prompt(prompt)
        if youtube_url:
            youtube_url = validation.validate_youtube_url(youtube_url)
        elif video_file:
            validation.is_allowed_file(video_file.filename)
        else:
            raise InvalidRequestError("Either YouTube URL or video file is required")
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise

    request_id = uuid.uuid4().hex
    request_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], request_id)
    os.makedirs(request_dir, exist_ok=True)

    try:
        video_path = video_processor.process_video_input(
            youtube_url=youtube_url, video_file=video_file, request_id=request_id
        )

        transcript = transcription.transcribe_video(video_path)

        moments = caption_selector.select_key_moments(transcript, prompt)
        if not moments:
            logger.warning("No matching moments found using both Gemini and fallback methods.")
            return jsonify({
                "error": "No matching moments found in the video",
                "request_id": request_id
            }), 404

        gif_paths = []
        output_dir = current_app.config["GIF_OUTPUT_DIR"]
        os.makedirs(output_dir, exist_ok=True)

        for i, moment in enumerate(moments[:3]):
            gif_filename = f"{request_id}_{i}.gif"
            gif_path = os.path.join(output_dir, gif_filename)
            gif_generator.generate_captioned_gif(
                video_path, moment["start"], moment["end"], moment["text"], gif_path
            )
            gif_paths.append({
                "id": i,
                "url": f"/api/gif/download/{gif_filename}",
                "caption": moment["text"],
                "start": moment["start"],
                "end": moment["end"],
                "duration": moment["end"] - moment["start"],
            })

        content_analysis = caption_selector.analyze_transcript_content(
            transcript, "Summarize the main themes in this video:"
        )

        return jsonify({
            "gifs": gif_paths,
            "request_id": request_id,
            "content_analysis": content_analysis,
        }), 200

    except Exception as e:
        logger.exception("GIF generation failed")
        raise

@bp.route("/download/<filename>", methods=["GET"])
def download_gif(filename):
    """
    Download a generated GIF.
    """
    gif_path = os.path.join(current_app.config["GIF_OUTPUT_DIR"], filename)
    if not os.path.exists(gif_path):
        logger.error(f"GIF not found: {gif_path}")
        return jsonify({"error": "GIF not found"}), 404

    logger.info(f"Serving GIF: {gif_path}")
    return send_file(gif_path, mimetype="image/gif")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.update(
        UPLOAD_FOLDER=tempfile.mkdtemp(),
        GIF_OUTPUT_DIR=tempfile.mkdtemp(),
        MAX_VIDEO_DURATION=600,
        WHISPER_MODEL="base",
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
        GIF_RESOLUTION=(640, 360), 
        MAX_GIF_DURATION=5,       
        GIF_FPS=10,               
    )

    app.register_blueprint(bp)

    try:
        print("Starting test server...")
        app.run(debug=True, port=5001)
    finally:
        shutil.rmtree(app.config["UPLOAD_FOLDER"])
        shutil.rmtree(app.config["GIF_OUTPUT_DIR"])
