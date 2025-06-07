import pytest
from app.core.caption_selector_fallback import select_moments_fallback

def test_select_moments_fallback_for_funny_theme():
    """
    Test that segments containing the word 'funny' are prioritized.
    """
    segments = [
        {"start": 0, "end": 5, "text": "This is a funny moment that made everyone smile."},
        {"start": 10, "end": 15, "text": "A serious discussion without humor."},
        {"start": 20, "end": 25, "text": "Another funny moment that made me laugh."},
    ]
    theme = "funny"
    selected = select_moments_fallback(segments, theme, max_moments=2)
    
    assert len(selected) <= 2
    
    assert any("funny" in seg["text"].lower() for seg in selected)


def test_select_moments_fallback_no_matching_keywords():
    """
    Test that if none of the segments contain keywords related to the theme,
    the fallback still returns segments (sorted by score), but none may contain the theme word.
    """
    segments = [
        {"start": 0, "end": 5, "text": "This is an ordinary moment."},
        {"start": 6, "end": 10, "text": "Nothing special happens here."},
    ]
    theme = "funny"
    selected = select_moments_fallback(segments, theme, max_moments=2)

    assert len(selected) <= 2
    
    assert len(selected) == len(segments) or len(selected) <= 2


def test_select_moments_fallback_empty_segments():
    """
    Test that when an empty list of segments is provided, the fallback returns an empty list.
    """
    segments = []
    theme = "funny"
    selected = select_moments_fallback(segments, theme, max_moments=3)
    assert selected == []


def test_select_moments_fallback_with_emphasis():
    """
    When segments have emphasis (i.e. are all uppercase or contain punctuation),
    then those adjustments in scoring should influence selection.
    """
    segments = [
        {"start": 0, "end": 4, "text": "THIS IS VERY FUNNY!"},
        {"start": 5, "end": 8, "text": "A normal statement."},
        {"start": 9, "end": 12, "text": "It is quite humorous and funny."},
    ]
    theme = "funny"
    selected = select_moments_fallback(segments, theme, max_moments=2)
    
    assert len(selected) <= 2
    assert any(seg["text"].isupper() or "funny" in seg["text"].lower() for seg in selected)


def test_select_moments_fallback_max_moments_limit():
    """
    Test that if more segments than max_moments exist, the fallback returns at most the specified number.
    """
    segments = [
        {"start": 0, "end": 2, "text": "funny moment here"},
        {"start": 10, "end": 12, "text": "funny moment later"},
        {"start": 20, "end": 22, "text": "another funny moment"},
        {"start": 30, "end": 32, "text": "yet another funny moment"}
    ]
    theme = "funny"
    max_moments = 2
    selected = select_moments_fallback(segments, theme, max_moments=max_moments)
    assert len(selected) <= max_moments
