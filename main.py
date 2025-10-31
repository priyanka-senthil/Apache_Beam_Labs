"""
Twitter Sentiment Analysis API - Minimal Version
Single tweet analysis only
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict
import re
from datetime import datetime


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

POSITIVE_WORDS = {
    'love', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 
    'brilliant', 'wonderful', 'happy', 'excited', 'best', 'good',
    'beautiful', 'perfect', 'grateful', 'thanks', 'helpful', 'easy',
    'outstanding', 'superb', 'enjoy', 'glad', 'nice', 'lovely'
}

NEGATIVE_WORDS = {
    'hate', 'terrible', 'worst', 'horrible', 'bad', 'annoying',
    'frustrated', 'angry', 'broken', 'fail', 'disappointed', 'disaster',
    'slow', 'complicated', 'waste', 'poor', 'awful', 'useless', 'sad'
}

NEGATION_WORDS = {'not', 'no', 'never', "don't", "doesn't", "didn't", "won't"}

POSITIVE_EMOJIS = {'😊', '🎉', '😃', '😄', '❤️', '👍', '✨', '🌟', '💪', '🔥', '✅'}
NEGATIVE_EMOJIS = {'😡', '😢', '😞', '😠', '💔', '👎', '😰', '😤', '😭', '😩', '❌'}


def analyze_sentiment(tweet: str) -> Dict:
    """
    Analyze sentiment of a single tweet
    Returns: sentiment, confidence, and detailed scores
    """
    original = tweet
    cleaned = tweet.lower()
    cleaned = re.sub(r'http\S+|www\S+', '', cleaned)  # Remove URLs
    
    words = cleaned.split()
    
    positive_score = 0
    negative_score = 0
    emoji_score = 0
    
    # Analyze words with negation handling
    negation_active = False
    
    for word in words:
        # Check for negation
        if word in NEGATION_WORDS:
            negation_active = True
            continue
        
        # Score positive words
        if word in POSITIVE_WORDS:
            if negation_active:
                negative_score += 1  # "not good" = negative
            else:
                positive_score += 1
            negation_active = False
        
        # Score negative words
        elif word in NEGATIVE_WORDS:
            if negation_active:
                positive_score += 1  # "not bad" = positive
            else:
                negative_score += 1
            negation_active = False
        
        # Reset negation after a few words
        elif negation_active:
            negation_active = False
    
    # Analyze emojis (weighted higher)
    for emoji in POSITIVE_EMOJIS:
        emoji_score += tweet.count(emoji) * 2
    
    for emoji in NEGATIVE_EMOJIS:
        emoji_score -= tweet.count(emoji) * 2
    
    # Calculate final scores
    total_positive = positive_score + max(0, emoji_score)
    total_negative = negative_score + abs(min(0, emoji_score))
    total_score = total_positive + total_negative
    
    # Determine sentiment and confidence
    if total_positive > total_negative:
        sentiment = 'POSITIVE'
        confidence = total_positive / (total_score + 1)
    elif total_negative > total_positive:
        sentiment = 'NEGATIVE'
        confidence = total_negative / (total_score + 1)
    else:
        sentiment = 'NEUTRAL'
        confidence = 0.5
    
    return {
        'tweet': original,
        'sentiment': sentiment,
        'confidence': round(confidence, 3),
        'positive_score': total_positive,
        'negative_score': total_negative,
        'emoji_score': emoji_score,
        'analysis_timestamp': datetime.now().isoformat()
    }


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TweetInput(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Tweet text to analyze",
        example="I love Apache Beam! 🎉 #apachebeam"
    )


class SentimentResponse(BaseModel):
    tweet: str
    sentiment: str
    confidence: float
    positive_score: int
    negative_score: int
    emoji_score: int
    analysis_timestamp: str


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Twitter Sentiment Analysis API",
    description="Analyze sentiment of tweets using Apache Beam",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API Root - Health check"""
    return {
        "status": "healthy",
        "message": "Twitter Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
            "docs": "GET /docs",
            "examples": "GET /examples"
        }
    }


@app.post("/analyze", response_model=SentimentResponse)
async def analyze_tweet(tweet: TweetInput):
    """
    Analyze sentiment of a single tweet
    
    **Example Request:**
    ```json
    {
        "text": "I love Apache Beam! 🎉"
    }
    ```
    
    **Response:**
    - sentiment: POSITIVE, NEGATIVE, or NEUTRAL
    - confidence: 0.0 to 1.0
    - positive_score: count of positive indicators
    - negative_score: count of negative indicators
    - emoji_score: emoji sentiment impact
    """
    try:
        result = analyze_sentiment(tweet.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/examples")
async def get_examples():
    """Get example tweets to try"""
    return {
        "examples": [
            {
                "text": "I love Apache Beam! It's amazing! 🎉",
                "expected": "POSITIVE"
            },
            {
                "text": "This is terrible 😡 #frustrated",
                "expected": "NEGATIVE"
            },
            {
                "text": "Apache Beam is great for big data #bigdata",
                "expected": "POSITIVE"
            },
            {
                "text": "Not bad, but could be better",
                "expected": "NEUTRAL or slightly POSITIVE"
            },
            {
                "text": "The documentation is not good 😞",
                "expected": "NEGATIVE"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Twitter Sentiment Analysis API")
    print("="*60)
    print("📖 Docs:      http://localhost:8000/docs")
    print("🌐 Interface: Open index.html in browser")
    print("🔌 Endpoint:  POST http://localhost:8000/analyze")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)