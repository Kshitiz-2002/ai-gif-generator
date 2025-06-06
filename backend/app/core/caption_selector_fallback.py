import re
import logging
import nltk
import math
from textblob import TextBlob
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize

logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

def get_keywords(theme):
    """Extract keywords from theme using NLP techniques"""
    tokens = word_tokenize(theme.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    expanded_keywords = set(keywords)
    for word in keywords:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                expanded_keywords.add(lemma.name().lower().replace('_', ' '))
    
    if "funny" in expanded_keywords:
        expanded_keywords.update(["humor", "joke", "laugh", "comedy"])
    if "sad" in expanded_keywords:
        expanded_keywords.update(["emotional", "tear", "depress", "unhappy"])
    if "motiv" in expanded_keywords:
        expanded_keywords.update(["inspire", "encourage", "empower", "drive"])
    
    return expanded_keywords

def score_segment(segment, keywords):
    """Score a transcript segment based on relevance to keywords"""
    text = segment['text'].lower()
    
    word_count = len(word_tokenize(text))
    keyword_count = sum(1 for word in keywords if word in text)
    keyword_density = keyword_count / word_count if word_count > 0 else 0
    
    sentiment = TextBlob(text).sentiment.polarity
    
    sentiment_weight = 1.0
    if any(word in keywords for word in ["sad", "depress", "tear"]):
        sentiment_weight = -1.0 
    elif any(word in keywords for word in ["funny", "humor", "joke"]):
        sentiment_weight = abs(sentiment)  
    
    sentences = sent_tokenize(text)
    avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences) if sentences else 0
    structure_score = 1 / (1 + avg_sentence_length) 
    
    position_score = 1 / (1 + segment['start']/60)  
    
    emphasis_score = 0
    if text.isupper():  
        emphasis_score += 0.5
    if any(punc in text for punc in ['!', '?']):  
        emphasis_score += 0.3
    if '"' in text or "'" in text: 
        emphasis_score += 0.2
    
 
    return (
        0.4 * keyword_density +
        0.2 * (sentiment * sentiment_weight + 1) + 
        0.15 * structure_score +
        0.15 * position_score +
        0.1 * min(emphasis_score, 1.0) 
    )

def select_moments_fallback(segments, theme, max_moments=3):
    """Fallback moment selection using NLP techniques"""
    try:
        keywords = get_keywords(theme)
        logger.debug(f"Keywords for theme '{theme}': {keywords}")
        
        scored_segments = []
        for segment in segments:
            score = score_segment(segment, keywords)
            scored_segments.append({
                **segment,
                "score": score
            })
        
        scored_segments.sort(key=lambda x: x['score'], reverse=True)
        
        selected = []
        min_separation = 15  
        for segment in scored_segments:
            if len(selected) >= max_moments:
                break
                
            too_close = any(
                abs(segment['start'] - s['start']) < min_separation
                for s in selected
            )
            
            if not too_close:
                selected.append({
                    "text": segment['text'],
                    "start": segment['start'],
                    "end": segment['end'],
                    "score": segment['score']
                })
        
        return [{"text": s["text"], "start": s["start"], "end": s["end"]} for s in selected]
        
    except Exception as e:
        logger.error(f"Fallback moment selection failed: {str(e)}")
        return segments[:max_moments]
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sample_segments = [
        {
            "text": "THIS IS A VERY FUNNY MOMENT THAT MADE ME LAUGH OUT LOUD!", 
            "start": 10,
            "end": 16,
        },
        {
            "text": "I was deeply moved by the inspirational speech which truly motivated my spirit.",
            "start": 20,
            "end": 26,
        },
        {
            "text": "The conversation was dull and uninteresting.",
            "start": 30,
            "end": 35,
        },
        {
            "text": "A hilarious joke was told that left everyone in stitches!",
            "start": 40,
            "end": 45,
        },
        {
            "text": "The sad scenes in the film brought tears to my eyes.",
            "start": 50,
            "end": 55,
        },
    ]

    test_theme = "funny motivational"
    print("Extracting moments for theme:", test_theme)
    selected_moments = select_moments_fallback(sample_segments, test_theme, max_moments=3)

    print("\nSelected Moments:")
    for idx, moment in enumerate(selected_moments, start=1):
        print(f"Moment {idx}:")
        print(f"   Start: {moment['start']}s")
        print(f"   End: {moment['end']}s")
        print(f"   Text: {moment['text']}")