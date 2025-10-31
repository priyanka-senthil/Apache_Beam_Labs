"""
Apache Beam Pipeline for Batch Tweet Analysis
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json
import tempfile
import os
from typing import List, Dict
from sentiment_analyzer import SentimentAnalyzer, ExtractHashtags, ExtractMentions


class TweetAnalysisPipeline:
    """Encapsulate Beam pipeline logic"""
    
    def __init__(self, tweets: List[str], output_dir: str = None):
        self.tweets = tweets
        self.output_dir = output_dir or tempfile.mkdtemp()
        self.results = {}
    
    def run(self) -> Dict:
        """
        Run the complete analysis pipeline
        
        Returns:
            dict: Comprehensive analysis results
        """
        # Create temporary input file
        input_file = os.path.join(self.output_dir, 'input_tweets.txt')
        with open(input_file, 'w', encoding='utf-8') as f:
            for tweet in self.tweets:
                f.write(tweet + '\n')
        
        # Run pipeline
        options = PipelineOptions()
        
        with beam.Pipeline(options=options) as pipeline:
            
            # Read and analyze tweets
            analyzed_tweets = (
                pipeline
                | 'Create tweets' >> beam.Create(self.tweets)
                | 'Analyze sentiment' >> beam.Map(SentimentAnalyzer.analyze)
            )
            
            # 1. Count sentiments
            sentiment_counts = (
                analyzed_tweets
                | 'Extract sentiment' >> beam.Map(lambda x: (x['sentiment'], 1))
                | 'Count sentiments' >> beam.CombinePerKey(sum)
                | 'Collect sentiments' >> beam.combiners.ToList()
            )
            
            # 2. Calculate average confidence
            avg_confidence = (
                analyzed_tweets
                | 'Extract confidence' >> beam.Map(
                    lambda x: (x['sentiment'], x['confidence']))
                | 'Group confidence' >> beam.GroupByKey()
                | 'Average confidence' >> beam.Map(
                    lambda x: (x[0], sum(x[1]) / len(list(x[1]))))
                | 'Collect confidence' >> beam.combiners.ToList()
            )
            
            # 3. Extract and count hashtags
            hashtag_counts = (
                analyzed_tweets
                | 'Extract hashtags' >> beam.ParDo(ExtractHashtags())
                | 'Count hashtags' >> beam.Map(lambda x: (x['hashtag'], 1))
                | 'Sum hashtags' >> beam.CombinePerKey(sum)
                | 'Top hashtags' >> beam.combiners.Top.Of(10, key=lambda x: x[1])
            )
            
            # 4. Extract and count mentions
            mention_counts = (
                analyzed_tweets
                | 'Extract mentions' >> beam.ParDo(ExtractMentions())
                | 'Count mentions' >> beam.Map(lambda x: (x['mention'], 1))
                | 'Sum mentions' >> beam.CombinePerKey(sum)
                | 'Top mentions' >> beam.combiners.Top.Of(10, key=lambda x: x[1])
            )
            
            # 5. Get high confidence tweets
            high_confidence = (
                analyzed_tweets
                | 'Filter high confidence' >> beam.Filter(
                    lambda x: x['confidence'] > 0.7)
                | 'Collect high confidence' >> beam.combiners.ToList()
            )
            
            # 6. Get samples by sentiment
            positive_samples = (
                analyzed_tweets
                | 'Filter positive' >> beam.Filter(
                    lambda x: x['sentiment'] == 'POSITIVE')
                | 'Sample positive' >> beam.combiners.Sample.FixedSizeGlobally(5)
            )
            
            negative_samples = (
                analyzed_tweets
                | 'Filter negative' >> beam.Filter(
                    lambda x: x['sentiment'] == 'NEGATIVE')
                | 'Sample negative' >> beam.combiners.Sample.FixedSizeGlobally(5)
            )
            
            # Collect all results
            (
                {
                    'sentiment_counts': sentiment_counts,
                    'avg_confidence': avg_confidence,
                    'hashtag_counts': hashtag_counts,
                    'mention_counts': mention_counts,
                    'high_confidence': high_confidence,
                    'positive_samples': positive_samples,
                    'negative_samples': negative_samples
                }
                | 'Combine results' >> beam.CoGroupByKey()
            )
        
        # Read results from pipeline
        return self._compile_results()
    
    def _compile_results(self) -> Dict:
        """Compile results into structured format"""
        # This is a simplified version
        # In production, you'd read from actual Beam outputs
        results = {
            'total_tweets': len(self.tweets),
            'sentiment_distribution': {},
            'top_hashtags': [],
            'top_mentions': [],
            'sample_tweets': {
                'positive': [],
                'negative': []
            }
        }
        
        # Quick analysis for API response
        for tweet in self.tweets:
            analysis = SentimentAnalyzer.analyze(tweet)
            sentiment = analysis['sentiment']
            results['sentiment_distribution'][sentiment] = \
                results['sentiment_distribution'].get(sentiment, 0) + 1
        
        return results


class StreamAnalyzer:
    """Analyze tweets in real-time (simplified)"""
    
    @staticmethod
    def analyze_single(tweet: str) -> Dict:
        """Analyze a single tweet"""
        return SentimentAnalyzer.analyze(tweet)
    
    @staticmethod
    def analyze_batch(tweets: List[str]) -> List[Dict]:
        """Analyze multiple tweets"""
        return [SentimentAnalyzer.analyze(tweet) for tweet in tweets]
    
    @staticmethod
    def get_statistics(analyses: List[Dict]) -> Dict:
        """Calculate statistics from analyses"""
        if not analyses:
            return {
                'total': 0,
                'sentiment_distribution': {},
                'average_confidence': 0
            }
        
        sentiment_counts = {}
        total_confidence = 0
        
        for analysis in analyses:
            sentiment = analysis['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_confidence += analysis['confidence']
        
        return {
            'total': len(analyses),
            'sentiment_distribution': sentiment_counts,
            'average_confidence': round(total_confidence / len(analyses), 3),
            'positive_percentage': round(
                (sentiment_counts.get('POSITIVE', 0) / len(analyses)) * 100, 2),
            'negative_percentage': round(
                (sentiment_counts.get('NEGATIVE', 0) / len(analyses)) * 100, 2),
            'neutral_percentage': round(
                (sentiment_counts.get('NEUTRAL', 0) / len(analyses)) * 100, 2)
        }