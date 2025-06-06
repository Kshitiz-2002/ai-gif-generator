from flask import jsonify

class InvalidRequestError(Exception):
    """Custom exception for invalid requests"""
    pass

class VideoProcessingError(Exception):
    """Custom exception for video processing failures"""
    pass

class TranscriptionError(Exception):
    """Custom exception for transcription failures"""
    pass

class CaptionSelectionError(Exception):
    """Custom exception for caption selection failures"""
    pass

class GIFGenerationError(Exception):
    """Custom exception for GIF generation failures"""
    pass

def register_error_handlers(app):
    @app.errorhandler(InvalidRequestError)
    def handle_invalid_request(error):
        return jsonify({"error": str(error)}), 400
        
    @app.errorhandler(VideoProcessingError)
    def handle_video_processing(error):
        return jsonify({"error": f"Video processing error: {str(error)}"}), 400
        
    @app.errorhandler(TranscriptionError)
    def handle_transcription(error):
        return jsonify({"error": f"Transcription error: {str(error)}"}), 500
        
    @app.errorhandler(CaptionSelectionError)
    def handle_caption_selection(error):
        return jsonify({"error": f"Caption selection error: {str(error)}"}), 500
        
    @app.errorhandler(GIFGenerationError)
    def handle_gif_generation(error):
        return jsonify({"error": f"GIF generation error: {str(error)}"}), 500
        
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), 404
        
    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f"Internal error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500