import logging
from app.services import gemini_service
from app.utils.error_handlers import CaptionSelectionError
from app.config import configuration
from .caption_selector_fallback import select_moments_fallback

logger = logging.getLogger(__name__)

def select_key_moments(transcript_segments, theme_prompt, max_moments=3):
    """
    Select key moments using Gemini if available, otherwise fallback to NLP
    """
    try:
        if configuration.GEMINI_API_KEY:
            logger.info("Using Gemini for moment selection")
            return gemini_service.select_key_moments(
                transcript_segments,
                theme_prompt,
                max_moments
            )
        else:
            logger.info("Using fallback NLP for moment selection")
            return select_moments_fallback(
                transcript_segments,
                theme_prompt,
                max_moments
            )
    except Exception as e:
        logger.error(f"Moment selection failed: {str(e)}")
        raise CaptionSelectionError(f"Caption selection error: {str(e)}")

def analyze_transcript_content(transcript, prompt):
    """Analyze transcript content using Gemini"""
    try:
        if configuration.GEMINI_API_KEY:
            transcript_text = "\n".join(
                f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}" 
                for seg in transcript
            )
            return gemini_service.analyze_content(prompt, transcript_text)
        else:
            keywords = " ".join(seg['text'] for seg in transcript[:10]).split()[:20]
            return " ".join(keywords)
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        return "Content analysis unavailable"
    

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)

    sample_transcript_segments = [
        {"start": 0, "end": 5, "text": "The introduction of the event was extremely inspiring."},
        {"start": 6, "end": 10, "text": "I felt uplifted by the motivational speech that followed."},
        {"start": 11, "end": 15, "text": "A surprising twist in the conversation provided great insight."},
        {"start": 16, "end": 20, "text": "The speaker emphasized the importance of perseverance."},
        {"start": 21, "end": 25, "text": "A humorous remark lightened the mood at just the right moment."},
    ]

    test_theme_prompt = "inspiring and motivational"

    print("Testing key moments selection:")
    try:
        key_moments = select_key_moments(sample_transcript_segments, test_theme_prompt, max_moments=3)
        print("Selected Key Moments:")
        for idx, moment in enumerate(key_moments, start=1):
            print(f"  Moment {idx}: Start - {moment.get('start')}s, End - {moment.get('end')}s")
            print(f"             Text: {moment.get('text')}")
    except CaptionSelectionError as e:
        print(f"Error in key moments selection: {e}")
        sys.exit(1)

    print("\nTesting transcript content analysis:")
    analysis_result = analyze_transcript_content(sample_transcript_segments, test_theme_prompt)
    print("Transcript Analysis Result:")
    print(analysis_result)