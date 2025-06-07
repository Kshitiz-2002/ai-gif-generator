import os
import tempfile
import json
import pytest
from flask import Flask
from app.routes import gif_routes

@pytest.fixture
def app():
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
        TESTING=True,
    )
    app.register_blueprint(gif_routes.bp)
    yield app
    import shutil
    shutil.rmtree(app.config["UPLOAD_FOLDER"])
    shutil.rmtree(app.config["GIF_OUTPUT_DIR"])

@pytest.fixture
def client(app):
    return app.test_client()

def test_generate_gif_endpoint(client, monkeypatch):
    """
    Test the /api/gif/generate endpoint using dummy implementations 
    for video processing, transcription, caption selection, and GIF generation.
    The dummy video file path returned for the download simulation is
    "app/core/output/segment_10_30.mp4".
    """
    dummy_video_path = "app/core/output/segment_10_30.mp4"
    if not os.path.exists(dummy_video_path):
        os.makedirs(os.path.dirname(dummy_video_path), exist_ok=True)
        with open(dummy_video_path, "wb") as f:
            f.write(b"dummy video content for testing")
    
    from app.core import video_processor, transcription, caption_selector, gif_generator
    
    monkeypatch.setattr(
        video_processor,
        "process_video_input",
        lambda youtube_url, video_file, request_id: dummy_video_path
    )
    
    dummy_transcript = [{"start": 0, "end": 2, "text": "Dummy segment with funny content"}]
    monkeypatch.setattr(
        transcription,
        "transcribe_video",
        lambda video_path: dummy_transcript
    )
    
    dummy_moment = [{"start": 0, "end": 2, "text": "Dummy segment with funny content"}]
    monkeypatch.setattr(
        caption_selector,
        "select_key_moments",
        lambda transcript, prompt, max_moments=3: dummy_moment
    )
    
    monkeypatch.setattr(
        gif_generator,
        "generate_captioned_gif",
        lambda video_path, start, end, caption, output_path: output_path
    )
    
    data = {
        "prompt": "funny moments",
        "youtube_url": "https://www.youtube.com/watch?v=HCDVN7DCzYE"
    }
    
    response = client.post("/api/gif/generate", data=data)
    
    assert response.status_code == 200, f"Response: {response.data}"
    
    resp_json = json.loads(response.data)
    
    assert "gifs" in resp_json, "Missing 'gifs' in response"
    assert isinstance(resp_json["gifs"], list)
    assert len(resp_json["gifs"]) > 0, "GIF list is empty"
    assert "content_analysis" in resp_json, "Missing 'content_analysis' in response"
    assert "request_id" in resp_json, "Missing 'request_id' in response"
    
    first_gif = resp_json["gifs"][0]
    for key in ["caption", "start", "end", "duration", "url"]:
        assert key in first_gif, f"Missing key '{key}' in GIF data"
