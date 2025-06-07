# tests/unit/test_video_processing.py

import os
import tempfile
import pytest
from app.core import video_processor
from app.utils.error_handlers import VideoProcessingError

def test_extract_video_segment_invalid_video(tmp_path):
    """
    Test that extracting a video segment from an invalid video file raises an error.
    """
    source_video = tmp_path / "dummy_video.mp4"
    source_video.write_bytes(b"not a valid video content")
    
    with pytest.raises(Exception):
        video_processor.extract_video_segment(str(source_video), start=0, end=10)


class DummyVideoFileClip:
    """
    A dummy replacement for moviepy.editor.VideoFileClip to simulate a successful
    video segment extraction without needing an actual video file.
    """
    def __init__(self, video_path):
        self.video_path = video_path

    def subclip(self, start, end):
        self.start = start
        self.end = end
        return self

    def write_videofile(self, output_file, codec, audio_codec):
        with open(output_file, "wb") as f:
            f.write(b"dummy video content")

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def test_extract_video_segment_valid(tmp_path, monkeypatch):
    """
    Test successful extraction of a video segment using a dummy video file.
    Uses the dummy file "app/core/output/segment_10_30.mp4" for testing.
    """
    dummy_video_file = os.path.join("app", "core", "output", "segment_10_30.mp4")
    
    if not os.path.exists(dummy_video_file):
        os.makedirs(os.path.dirname(dummy_video_file), exist_ok=True)
        with open(dummy_video_file, "wb") as f:
            f.write(b"dummy content for segment extraction test")
    
    monkeypatch.setattr(video_processor, "VideoFileClip", DummyVideoFileClip)
    
    output_dir = str(tmp_path)
    output_file = video_processor.extract_video_segment(dummy_video_file, start=5, end=10, output_dir=output_dir)
    
    assert os.path.exists(output_file)
    with open(output_file, "rb") as f:
        content = f.read()
    assert b"dummy video content" in content

def test_process_video_input_youtube(monkeypatch, tmp_path):
    """
    Test process_video_input when a YouTube URL is provided.
    Monkey-patch the youtube_service.download_youtube_video function to return a dummy file.
    """
    def dummy_download_youtube_video(youtube_url, max_duration, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        dummy_path = os.path.join(output_dir, "dummy_downloaded_video.mp4")
        with open(dummy_path, "wb") as f:
            f.write(b"dummy youtube video content")
        return dummy_path

    dummy_module = type("dummy_module", (), {"download_youtube_video": dummy_download_youtube_video})
    monkeypatch.setattr(video_processor, "youtube_service", dummy_module)

    request_id = "test123"
    upload_dir = tmp_path / request_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_processor.process_video_input(
        youtube_url="https://www.youtube.com/watch?v=HCDVN7DCzYE", 
        video_file=None, 
        request_id=request_id
    )
    
    assert os.path.exists(video_path)
    with open(video_path, "rb") as f:
        content = f.read()
    assert b"dummy youtube video content" in content

def test_process_video_input_no_source():
    """
    Test process_video_input raises VideoProcessingError when no video source is provided.
    """
    with pytest.raises(VideoProcessingError):
        video_processor.process_video_input(youtube_url=None, video_file=None, request_id="dummy")
