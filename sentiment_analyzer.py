"""
Sentiment Analysis Module
Reusable sentiment analysis logic for Apache Beam pipelines
"""

import re
from typing import Dict, List, Tuple
import apache_beam as beam


# Sentiment lexicons
POSITIVE_WORDS = {
    'love', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 
    'brilliant', 'wonderful', 'happy', 'excited', 'best', 'good',
    'beautiful', 'perfect', 'grateful', 'thanks', 'helpful', 'easy',
    'revolutionary', 'successful', 'achievement', 'proud', 'enjoying',
    'intuitive', 'clean', 'efficient', 'appreciate', 'inspiring',
    'outstanding', 'incredible', 'superb', 'delighted', 'impressive'
}

NEGATIVE_WORDS = {
    'hate', 'terrible', 'worst', 'horrible', 'bad', 'annoying',
    'frustrated', 'angry', 'broken', 'fail', 'disappointed', 'disaster',
    'exhausted', 'stressed', 'confused', 'difficult', 'unreliable',
    'buggy', 'slow', 'complicated', 'waste', 'embarrassing', 'nightmare',
    'devastating', 'poor', 'confusing', 'ignored', 'issues', 'awful',
    'useless', 'pathetic', 'sucks', 'annoyed', 'irritating'
}

NEGATION_WORDS = {
    'not', 'no', 'never', 'neither', 'nobody', 'nothing', 
    "don't", "doesn't", "didn't", "won't", "wouldn't", "can't"
}

POSITIVE_EMOJIS = {'😊', '🎉', '😃', '😄', '❤️', '👍', '🎓', '✨', '🌟', '💪', '🔥', '✅'}
NEGATIVE_EMOJIS = {'😡', '😢', '😞', '😠', '💔', '👎', '😰', '😤', '😭', '😩', '❌'}


class SentimentAnalyzer:
    """Advanced sentiment analyzer with negation handling"""
    
    @staticmethod
    def clean_tweet(tweet: str) -> str:
        """Clean tweet text while preserving important elements"""
        cleaned = tweet.lower()
        cleaned = re.sub(r'http\S+|www\S+', '', cleaned)  # Remove URLs
        return cleaned.strip()
    
    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Extract words from text"""
        text = re.sub(r'[^\w\s#@😊🎉😃😄❤️👍🎓✨🌟😡😢😞😠💔👎😰😤💪🔥✅😭😩❌]', '', text)
        return text.split()
    
    @staticmethod
    def analyze(tweet: str) -> Dict:
        """
        Perform comprehensive sentiment analysis
        
        Returns:
            dict: {
                'tweet': original tweet,
                'sentiment': POSITIVE/NEGATIVE/NEUTRAL,
                'confidence': 0.0-1.0,
                'positive_score': int,
                'negative_score': int,
                'emoji_score': int,
                'cleaned': cleaned text
            }
        """
        original = tweet
        cleaned = SentimentAnalyzer.clean_tweet(tweet)
        words = SentimentAnalyzer.extract_words(cleaned)
        
        positive_score = 0
        negative_score = 0
        emoji_score = 0
        
        # Analyze words with negation handling
        negation_active = False
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Check for negation
            if word_lower in NEGATION_WORDS:
                negation_active = True
                continue
            
            # Score positive words
            if word_lower in POSITIVE_WORDS:
                if negation_active:
                    negative_score += 1  # Flip sentiment
                else:
                    positive_score += 1
                negation_active = False
            
            # Score negative words
            elif word_lower in NEGATIVE_WORDS:
                if negation_active:
                    positive_score += 1  # Flip sentiment
                else:
                    negative_score += 1
                negation_active = False
            
            # Reset negation after 2 words
            elif negation_active:
                negation_active = False
        
        # Analyze emojis (weighted more heavily)
        for emoji in POSITIVE_EMOJIS:
            emoji_score += tweet.count(emoji) * 2
        
        for emoji in NEGATIVE_EMOJIS:
            emoji_score -= tweet.count(emoji) * 2
        
        # Calculate final scores
        total_positive = positive_score + max(0, emoji_score)
        total_negative = negative_score + abs(min(0, emoji_score))
        
        # Determine sentiment and confidence
        total_score = total_positive + total_negative
        
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
            'cleaned': cleaned
        }


class ExtractHashtags(beam.DoFn):
    """Beam DoFn to extract hashtags"""
    
    def process(self, tweet_dict):
        hashtags = re.findall(r'#(\w+)', tweet_dict['cleaned'])
        for tag in hashtags:
            yield {
                'hashtag': tag.lower(),
                'sentiment': tweet_dict['sentiment'],
                'count': 1
            }


class ExtractMentions(beam.DoFn):
    """Beam DoFn to extract mentions"""
    
    def process(self, tweet_dict):
        mentions = re.findall(r'@(\w+)', tweet_dict['cleaned'])
        for mention in mentions:
            yield {
                'mention': mention.lower(),
                'sentiment': tweet_dict['sentiment'],
                'count': 1
            }


class CalculateStatistics(beam.DoFn):
    """Beam DoFn to calculate various statistics"""
    
    def process(self, tweet_dict):
        yield {
            'sentiment': tweet_dict['sentiment'],
            'word_count': len(tweet_dict['tweet'].split()),
            'has_hashtag': '#' in tweet_dict['tweet'],
            'has_mention': '@' in tweet_dict['tweet'],
            'has_emoji': any(e in tweet_dict['tweet'] for e in POSITIVE_EMOJIS | NEGATIVE_EMOJIS),
            'confidence': tweet_dict['confidence']
        }