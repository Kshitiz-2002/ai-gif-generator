import os
import sys
import logging
import imageio
import tempfile
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from app.config import configuration
from app.utils.error_handlers import GIFGenerationError
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

logger = logging.getLogger(__name__)

def generate_captioned_gif(video_path: str, start: float, end: float, caption: str, output_path: str) -> str:
    """Generate GIF with captions using optimized methods"""
    try:
        duration = end - start
        max_duration = configuration.MAX_GIF_DURATION
        if duration > max_duration:
            end = start + max_duration
            logger.warning(f"Trimming GIF duration to {max_duration}s")
        
        with VideoFileClip(video_path) as video:
            clip = video.subclip(start, end)
            
            if configuration.GIF_RESOLUTION:
                clip = clip.resize(configuration.GIF_RESOLUTION)
            
            txt_clip = create_optimized_caption(caption, clip.size, clip.duration)
            
            final_clip = CompositeVideoClip([clip, txt_clip])
            
            generate_optimized_gif(final_clip, output_path, configuration.GIF_FPS)
        
        logger.info(f"GIF generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"GIF generation failed: {str(e)}")
        raise GIFGenerationError(f"Video processing error: {str(e)}")

def create_optimized_caption(text, video_size, duration):
    """Create an optimized text caption with better readability.
    
    This version adds extra vertical padding and applies a stroke to the text,
    ensuring that multi-line captions are fully visible and clearer on the video.
    """
    width, height = video_size
    font_size = max(20, int(height * 0.05))
    max_width = int(width * 0.9)
    
    # Attempt to load Arial. Fall back if not found.
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        logger.warning("Arial font not found; falling back to default font.")
        font = ImageFont.load_default()
    
    # Prepare a temporary image to measure text dimensions.
    test_img = Image.new('RGB', (10, 10))
    test_draw = ImageDraw.Draw(test_img)
    
    lines = []
    words = text.split()
    current_line = ""
    
    # Break the text into lines so that each line fits within max_width.
    for word in words:
        test_line = current_line + (" " + word if current_line else word)
        text_width = test_draw.textlength(test_line, font=font)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Add extra vertical padding for clarity.
    vertical_padding = 10
    line_spacing = 5
    text_height = len(lines) * (font_size + line_spacing) + vertical_padding * 2
    
    # Create a transparent image with extra padding
    text_img = Image.new('RGBA', (width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    
    # Starting y coordinate includes the extra padding.
    y_text = vertical_padding
    # Stroke properties for better clarity (adjust stroke_width as needed)
    stroke_width = 2
    stroke_fill = "black"
    
    # Draw each line with center alignment and a stroke
    for line in lines:
        # Use the center of the image width and current y coordinate.
        draw.text(
            (width // 2, y_text),
            line,
            font=font,
            fill="white",
            anchor="mm",
            stroke_width=stroke_width,
            stroke_fill=stroke_fill
        )
        y_text += font_size + line_spacing
    
    # Create an image clip from the text image and position it at the bottom.
    text_clip = ImageClip(np.array(text_img)).set_duration(duration).set_position(("center", "bottom"))
    return text_clip

def generate_optimized_gif(clip, output_path, fps):
    """
    Generate an optimized GIF with better quality and smaller size.
    
    This function writes the given video clip to a temporary MP4 file using a unique filename,
    then uses imageio to read the temporary video and generate the GIF. After completion, it
    properly closes all file handles and removes the temporary file.
    
    Args:
        clip: The video clip (MoviePy clip) to convert into a GIF.
        output_path: The path where the resulting GIF will be saved.
        fps: Frames per second for both video writing and GIF generation.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_filename = temp_file.name

    # Write the video clip to the temporary file.
    clip.write_videofile(
        temp_filename, 
        fps=fps, 
        codec="libx264", 
        audio_codec="aac", 
        verbose=False
    )
    
    with imageio.get_reader(temp_filename) as reader:
        with imageio.get_writer(output_path, fps=fps, palettesize=256, quantizer="kraken", subrectangles=True) as writer:
            for frame in reader:
                writer.append_data(frame)
    
    os.remove(temp_filename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, "output", "segment_10_30.mp4")
    
    if not os.path.exists(video_path):
        print(f"Sample video not found at: {video_path}")
        sys.exit(1)
    
    start_time = 0      
    end_time = 10       
    caption = "This is a sample caption for our GIF."
    output_path = os.path.join(base_dir, "output", "output_sample.gif")
    
    try:
        result = generate_captioned_gif(video_path, start_time, end_time, caption, output_path)
        print(f"GIF generated successfully: {result}")
    except Exception as e:
        print(f"GIF generation failed: {str(e)}")
        sys.exit(1)
