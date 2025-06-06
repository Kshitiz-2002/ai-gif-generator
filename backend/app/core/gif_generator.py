import os
import sys
import logging
import imageio
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
    """Create an optimized text caption with better rendering"""    
    width, height = video_size
    font_size = max(20, int(height * 0.05))
    max_width = int(width * 0.9)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        logger.warning("Arial font not found; falling back to default font.")
        font = ImageFont.load_default()
    
    test_img = Image.new('RGB', (10, 10))
    test_draw = ImageDraw.Draw(test_img)
    
    lines = []
    words = text.split()
    current_line = ""
    
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
    
    text_height = len(lines) * (font_size + 5)
    text_img = Image.new('RGBA', (width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    
    y_text = 0
    for line in lines:
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                draw.text((width//2 + dx, y_text + dy), line, font=font, fill="black", anchor="mm")
        draw.text((width//2, y_text), line, font=font, fill="white", anchor="mm")
        y_text += font_size + 5
    
    text_clip = ImageClip(np.array(text_img)).set_duration(duration).set_position(("center", "bottom"))
    return text_clip

def generate_optimized_gif(clip, output_path, fps):
    """Generate optimized GIF with better quality and smaller size"""
    clip.write_videofile("temp.mp4", fps=fps, codec="libx264", audio_codec="aac")
    
    reader = imageio.get_reader("temp.mp4")
    writer = imageio.get_writer(output_path, fps=fps, palettesize=256, quantizer="kraken", subrectangles=True)
    
    for frame in reader:
        writer.append_data(frame)
    
    writer.close()
    os.remove("temp.mp4")

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
