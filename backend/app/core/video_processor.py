import os
import uuid 
import logging
from app.services import youtube_service
from app.utils import storage, validation
from app.utils.error_handlers import VideoProcessingError
from app.config import configuration

logger = logging.getLogger(__name__)

def process_video_input(youtube_url=None, video_file=None, request_id=None):
    """
    Process video input from either YouTube URL or file upload.
    Returns the path to the processed video file.
    """
    try:
        if youtube_url:
            logger.info(f"Processing YouTube URL: {youtube_url}")
            validation.validate_youtube_url(youtube_url)
            return youtube_service.download_youtube_video(
                youtube_url,
                max_duration=configuration.MAX_VIDEO_DURATION,
                output_dir=os.path.join(configuration.UPLOAD_FOLDER, request_id)
            )
        elif video_file:
            logger.info("Processing uploaded video file")
            return storage.save_uploaded_file(video_file, request_id)
        else:
            raise VideoProcessingError("No valid video source provided")
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}")
        raise VideoProcessingError(f"Video processing error: {str(e)}")


def extract_video_segment(video_path, start, end, output_dir=None):
    """
    Extracts a segment from a video file and saves it in the specified output directory.
    If no output_dir is provided, a folder named 'output' in the same directory as the script is used.
    
    Parameters:
      video_path (str): Path to the source video file.
      start (int/float): The start time (in seconds) for the segment.
      end (int/float): The end time (in seconds) for the segment.
      output_dir (str): Optional directory where the segment should be saved.
      
    Returns:
      output_file (str): The path to the saved video segment.
    """
    try:
        from moviepy import VideoFileClip
        with VideoFileClip(video_path) as video:
            segment = video.subclipped(start, end)
            
            # Determine the output directory; default to an "output" folder in the same directory as this script.
            if output_dir is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.join(base_dir, "output")
            
            # Ensure that the output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Create an output file name. Including start and end times helps prevent overwrites.
            output_file = os.path.join(output_dir, f"segment_{start}_{end}.mp4")
            
            segment.write_videofile(output_file, codec="libx264", audio_codec="aac")
            return output_file
    except Exception as e:
        logger.error(f"Video segment extraction failed: {str(e)}")
        raise VideoProcessingError(f"Segment extraction failed: {str(e)}")
    

if __name__ == "__main__":
    import sys

    # Example inputs for testing
    youtube_url = "https://www.youtube.com/watch?v=HCDVN7DCzYE"
    video_file = None  # Use a valid file if you want to test file uploads
    request_id = "test_request_123"  # Alternatively, generate a unique id with: str(uuid.uuid4())

    try:
        # Test video processing
        processed_video_path = process_video_input(youtube_url=youtube_url, video_file=video_file, request_id=request_id)
        print(f"Processed video saved at: {processed_video_path}")

        # Set the output directory within your project structure (an "output" folder)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "output")
        
        # Test video segment extraction
        start_time, end_time = 10, 30  # Example start and end times in seconds
        extracted_segment = extract_video_segment(processed_video_path, start_time, end_time, output_dir=output_dir)
        print(f"Extracted video segment saved at: {extracted_segment}")

    except VideoProcessingError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
