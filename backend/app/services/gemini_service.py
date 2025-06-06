import os
import json
import logging
from typing import List, Dict

import google.generativeai as genai
from app.utils.error_handlers import CaptionSelectionError

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

_model = None


def _init_gemini_model():
    """
    Initialize (or reuse) the Gemini generative model.
    Raises CaptionSelectionError if initialization fails.
    """
    global _model

    if _model is not None:
        return

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set in environment")
        raise CaptionSelectionError("Gemini API key not provided")

    try:
        logger.info(f"Configuring Gemini client with model '{GEMINI_MODEL_NAME}'...")
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        logger.info("Gemini model initialized successfully.")
    except Exception as e:
        logger.error(f"Gemini model initialization failed: {e}")
        raise CaptionSelectionError("Failed to initialize Gemini model")


def select_key_moments(
    transcript_segments: List[Dict[str, float]],
    theme_prompt: str,
    max_moments: int = 3
) -> List[Dict[str, float]]:
    """
    Use the Gemini model to select key transcript segments matching the given theme.
    Args:
        transcript_segments: List of dicts with keys "start", "end", "text".
        theme_prompt: A short string describing the desired theme (e.g., "funny moments").
        max_moments: Maximum number of segments to return.

    Returns:
        A list of up to `max_moments` dicts, each containing:
            {
                "start": float,   # segment start time (seconds)
                "end": float,     # segment end time (seconds)
                "text": str       # transcript text for that segment
            }
    Raises:
        CaptionSelectionError: if Gemini fails or parsing the output fails.
    """
    _init_gemini_model()

    transcript_text = ""
    for seg in transcript_segments:
        start_ts = seg.get("start", 0.0)
        end_ts = seg.get("end", 0.0)
        text = seg.get("text", "").replace("\n", " ").strip()
        transcript_text += f"[{start_ts:.1f}-{end_ts:.1f}] {text}\n"

    system_prompt = (
        f"You are a transcript analyzer. Select the top {max_moments} segments "
        f"related to the theme '{theme_prompt}'.\n"
        "Return ONLY this JSON format, with no extra commentary:\n"
        "{\n"
        "  \"moments\": [\n"
        "    {\"start\": float, \"end\": float, \"text\": string},\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
    )

    full_prompt = system_prompt + transcript_text

    try:
        response = _model.generate_content(full_prompt)
        raw_text = response.text.strip()
        data = json.loads(raw_text)
    except Exception:
        try:
            logger.warning("Direct JSON parse failed; attempting to extract JSON block from response.")
            start_idx = raw_text.index("{")
            end_idx = raw_text.rindex("}") + 1
            snippet = raw_text[start_idx:end_idx]
            data = json.loads(snippet)
        except Exception as ee:
            logger.error(f"Gemini JSON parse failed: {ee}\nRaw response:\n{raw_text}")
            raise CaptionSelectionError("Failed to parse JSON from Gemini output")

    moments = data.get("moments", [])
    if not isinstance(moments, list):
        raise CaptionSelectionError("Invalid Gemini format: 'moments' is not a list")

    cleaned: List[Dict[str, float]] = []
    for i, moment in enumerate(moments):
        if i >= max_moments:
            break
        try:
            start_val = float(moment["start"])
            end_val = float(moment["end"])
            text_val = str(moment["text"]).strip()
            cleaned.append({"start": start_val, "end": end_val, "text": text_val})
        except Exception as parse_err:
            logger.warning(f"Skipping invalid moment entry {moment}: {parse_err}")
            continue

    return cleaned


def analyze_content(prompt: str, content: str) -> str:
    """
    General-purpose content analysis or summarization using Gemini.
    Args:
        prompt: The instruction for Gemini (e.g., "Summarize this transcript:").
        content: The body of text to analyze (e.g., the concatenated transcript).

    Returns:
        A plain-text string response from Gemini.
    Raises:
        CaptionSelectionError: if the Gemini call fails.
    """
    _init_gemini_model()

    system_prompt = (
        "You are a helpful assistant that analyzes content. Follow the instructions "
        "and respond in plain text.\n\n"
    )
    full_prompt = system_prompt + prompt.strip() + "\n\n" + content.strip()

    try:
        response = _model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini analyze_content call failed: {e}")
        raise CaptionSelectionError("Gemini content analysis failed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_segments = [
        {"start": 15.0, "end": 16.5, "text": "She started crying during the ceremony"},
        {"start": 25.2, "end": 27.0, "text": "Everyone laughed so hard"},
        {"start": 42.0, "end": 43.7, "text": "He proposed unexpectedly"},
    ]

    print("\n=== Testing select_key_moments ===")
    try:
        moments = select_key_moments(
            transcript_segments=test_segments,
            theme_prompt="emotional moments",
            max_moments=2
        )
        for idx, m in enumerate(moments, 1):
            print(f"Moment {idx}: {m['start']:.1f}-{m['end']:.1f} → {m['text']}")
    except Exception as e:
        print(f"select_key_moments failed: {e}")

    print("\n=== Testing analyze_content ===")
    prompt_text = "Summarize this video transcript:"
    transcript_body = "\n".join(seg["text"] for seg in test_segments)
    try:
        summary = analyze_content(prompt_text, transcript_body)
        print("Summary:", summary)
    except Exception as e:
        print(f"analyze_content failed: {e}")
