import os
import tempfile
import uuid
import logging
from moviepy.editor import VideoFileClip

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError

from app.utils.error_handlers import VideoProcessingError

logger = logging.getLogger(__name__)


def get_video_metadata(url):
    """
    Get metadata for a YouTube video using yt-dlp (no download).

    Args:
        url (str): YouTube URL

    Returns:
        dict: Video metadata (title, uploader, duration, thumbnail, view_count)
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "forcejson": True,
        # Mimic a modern browser User-Agent to improve compatibility with YouTube
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/137.0.0.0 Safari/537.36",
        # Bypass geographic restrictions if possible
        "geo_bypass": True,
        # Setting a Referer header similar to a normal browser request
        "http_headers": {
            "Referer": "https://www.youtube.com",
        },
        "youtube_include_dash_manifest": False,
        "cookiefile": "/path/to/cookies.txt",
    }
    try:
        logger.info(f"Fetching metadata for: {url} using yt-dlp")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "author": info.get("uploader"),
            "length": info.get("duration"),
            "thumbnail_url": info.get("thumbnail"),
            "views": info.get("view_count"),
        }
    except (DownloadError, ExtractorError, Exception) as e:
        logger.error(f"yt-dlp metadata fetch failed: {e}")
        raise VideoProcessingError(f"YouTube metadata fetch failed: {e}")


def download_youtube_video(url, max_duration=None, output_dir=None):
    """
    Download YouTube video with output directory support.
    """
    try:
        meta = get_video_metadata(url)
    except VideoProcessingError:
        raise

    length = meta.get("length", 0)
    if max_duration is not None and length and length > max_duration:
        raise VideoProcessingError(
            f"Video duration ({length}s) exceeds allowed max ({max_duration}s)"
        )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        temp_path = os.path.join(output_dir, f"yt_{uuid.uuid4().hex}.mp4")
    else:
        temp_path = tempfile.mktemp(suffix=".mp4")

    ydl_opts = {
        "outtmpl": temp_path,
        "format": "best[ext=mp4]",
        "quiet": True,
        "noprogress": True,
        # Use the same custom User-Agent for downloads
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/137.0.0.0 Safari/537.36",
        "geo_bypass": True,
        "http_headers": {
            "Referer": "https://www.youtube.com",
        },
        "youtube_include_dash_manifest": False,
        "cookiefile": "/path/to/cookies.txt",
    }

    try:
        logger.info(f"Downloading YouTube video: {url}")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(temp_path):
            raise VideoProcessingError(f"Expected download at {temp_path} not found")

        logger.info(f"Downloaded to: {temp_path}")
        return temp_path

    except (DownloadError, ExtractorError, Exception) as e:
        logger.error(f"yt-dlp download failed: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise VideoProcessingError(f"YouTube download failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_url = "https://www.youtube.com/watch?v=HCDVN7DCzYE"

    print("Testing yt-dlp YouTube service...")

    print("\nTesting metadata retrieval (yt-dlp):")
    try:
        md = get_video_metadata(test_url)
        print("Metadata:")
        for k, v in md.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"Metadata test failed: {e}")

    print("\nTesting video download (yt-dlp):")
    try:
        path = download_youtube_video(test_url, max_duration=600)
        print(f"Downloaded to: {path}")

        with VideoFileClip(path) as clip:
            print(f"Duration: {clip.duration} seconds")
            print(f"Resolution: {clip.size}")

        os.remove(path)
        print("Temporary file deleted.")
    except Exception as e:
        print(f"Download test failed: {e}")
