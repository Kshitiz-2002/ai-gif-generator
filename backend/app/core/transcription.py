import os
import logging
import sys
import whisper
from whisper.utils import get_writer
from app.config import configuration
from app.utils.error_handlers import TranscriptionError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_model_cache = {}

def transcribe_video(video_path: str) -> list:
    """Transcribe video using Whisper with advanced options"""
    try:
        model_name = configuration.WHISPER_MODEL
        if model_name not in _model_cache:
            logger.info(f"Loading Whisper model: {model_name}")
            _model_cache[model_name] = whisper.load_model(model_name)
        
        model = _model_cache[model_name]
        logger.info(f"Starting transcription for: {video_path}")
        
        result = model.transcribe(
            video_path,
            verbose=False,
            word_timestamps=True,
            fp16=False 
        )
        
        segments = result.get("segments", [])
        for seg in segments:
            seg['duration'] = seg['end'] - seg['start']
            seg['word_count'] = len(seg['text'].split())
        
        logger.info(f"Transcription completed with {len(segments)} segments")
        return segments
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise TranscriptionError(f"Transcription service unavailable: {str(e)}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, "output", "segment_10_30.mp4")
    
    if not os.path.exists(video_path):
        print(f"Test video not found at: {video_path}")
        sys.exit(1)

    try:
        segments = transcribe_video(video_path)
        print("Transcription segments:")
        for idx, seg in enumerate(segments, start=1):
            print(f"\nSegment {idx}:")
            print(f"  Start: {seg['start']}s")
            print(f"  End: {seg['end']}s")
            print(f"  Duration: {seg['duration']}s")
            print(f"  Word Count: {seg['word_count']}")
            print(f"  Text: {seg['text']}")
    except TranscriptionError as te:
        print(f"Error: {str(te)}")
        sys.exit(1)
