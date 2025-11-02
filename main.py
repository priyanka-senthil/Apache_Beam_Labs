"""
Twitter Sentiment Analysis API with Apache Beam & FastAPI
NOW WITH FILE OUTPUT SUPPORT!
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import re
import os
import glob
from datetime import datetime

from sentiment_analyzer import SentimentAnalyzer
from beam_pipeline import StreamAnalyzer

# Import Apache Beam for file output
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Tweet(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="Tweet text")
    tweet_id: Optional[str] = None
    user: Optional[str] = None
    timestamp: Optional[str] = None


class TweetBatch(BaseModel):
    tweets: List[str] = Field(..., min_items=1, max_items=1000, 
                              description="List of tweet texts")


class SentimentResponse(BaseModel):
    tweet: str
    sentiment: str
    confidence: float
    positive_score: int
    negative_score: int
    emoji_score: int
    analysis_timestamp: str


class BatchAnalysisResponse(BaseModel):
    total_analyzed: int
    sentiment_distribution: Dict[str, int]
    average_confidence: float
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    analyses: List[SentimentResponse]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Twitter Sentiment Analysis API",
    description="Advanced sentiment analysis powered by Apache Beam with file output support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IN-MEMORY STORAGE
analysis_history = []

# Ensure output directory exists
os.makedirs('output', exist_ok=True)


# ============================================================================
# HELPER FUNCTION - BEAM PIPELINE THAT WRITES FILES
# ============================================================================

def run_beam_pipeline_with_files(tweets: List[str], output_dir: str = "output"):
    """
    Run Apache Beam pipeline that writes analysis results to files
    
    This creates multiple output files:
    - sentiment_counts-*
    - top_hashtags-*
    - positive_samples-*
    - negative_samples-*
    """
    
    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    options = PipelineOptions()
    
    with beam.Pipeline(options=options) as pipeline:
        
        # Analyze all tweets
        analyzed_tweets = (
            pipeline
            | 'Create tweets' >> beam.Create(tweets)
            | 'Analyze sentiment' >> beam.Map(SentimentAnalyzer.analyze)
        )
        
        # 1. Count sentiments and write to file
        (
            analyzed_tweets
            | 'Extract sentiment' >> beam.Map(lambda x: (x['sentiment'], 1))
            | 'Count sentiments' >> beam.CombinePerKey(sum)
            | 'Format counts' >> beam.Map(lambda x: f"{x[0]}: {x[1]} tweets")
            | 'Write sentiment counts' >> beam.io.WriteToText(
                f'{output_dir}/sentiment_counts_{timestamp}',
                num_shards=1,
                shard_name_template=''
            )
        )
        
        # 2. Extract hashtags and write to file
        (
            analyzed_tweets
            | 'Extract hashtags' >> beam.FlatMap(
                lambda x: re.findall(r'#(\w+)', x['cleaned']))
            | 'Pair hashtags' >> beam.Map(lambda x: (x.lower(), 1))
            | 'Count hashtags' >> beam.CombinePerKey(sum)
            | 'Top hashtags' >> beam.combiners.Top.Of(10, key=lambda x: x[1])
            | 'Format hashtags' >> beam.FlatMap(
                lambda items: [f"#{tag}: {count} times" for tag, count in items])
            | 'Write hashtags' >> beam.io.WriteToText(
                f'{output_dir}/top_hashtags_{timestamp}',
                num_shards=1,
                shard_name_template=''
            )
        )
        
        # 3. Get positive tweet samples and write to file
        (
            analyzed_tweets
            | 'Filter positive' >> beam.Filter(lambda x: x['sentiment'] == 'POSITIVE')
            | 'Sample positive' >> beam.combiners.Sample.FixedSizeGlobally(10)
            | 'Format positive' >> beam.FlatMap(
                lambda samples: [f"[{s['confidence']:.2f}] {s['tweet']}" for s in samples])
            | 'Write positive' >> beam.io.WriteToText(
                f'{output_dir}/positive_samples_{timestamp}',
                num_shards=1,
                shard_name_template=''
            )
        )
        
        # 4. Get negative tweet samples and write to file
        (
            analyzed_tweets
            | 'Filter negative' >> beam.Filter(lambda x: x['sentiment'] == 'NEGATIVE')
            | 'Sample negative' >> beam.combiners.Sample.FixedSizeGlobally(10)
            | 'Format negative' >> beam.FlatMap(
                lambda samples: [f"[{s['confidence']:.2f}] {s['tweet']}" for s in samples])
            | 'Write negative' >> beam.io.WriteToText(
                f'{output_dir}/negative_samples_{timestamp}',
                num_shards=1,
                shard_name_template=''
            )
        )
        
        # 5. Write detailed analysis to file
        (
            analyzed_tweets
            | 'Format detailed' >> beam.Map(
                lambda x: json.dumps({
                    'tweet': x['tweet'],
                    'sentiment': x['sentiment'],
                    'confidence': x['confidence'],
                    'scores': {
                        'positive': x['positive_score'],
                        'negative': x['negative_score'],
                        'emoji': x['emoji_score']
                    }
                }))
            | 'Write detailed' >> beam.io.WriteToText(
                f'{output_dir}/detailed_analysis_{timestamp}',
                num_shards=1,
                shard_name_template=''
            )
        )
    
    return timestamp


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/analyze/single", response_model=SentimentResponse)
async def analyze_single_tweet(tweet: Tweet):
    """Analyze a single tweet (returns JSON, no files)"""
    try:
        result = SentimentAnalyzer.analyze(tweet.text)
        result['analysis_timestamp'] = datetime.now().isoformat()
        
        analysis_history.append({
            'tweet': tweet.text,
            'sentiment': result['sentiment'],
            'timestamp': result['analysis_timestamp']
        })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_tweets(batch: TweetBatch):
    """Analyze multiple tweets (returns JSON, no files)"""
    try:
        analyses = StreamAnalyzer.analyze_batch(batch.tweets)
        
        for analysis in analyses:
            analysis['analysis_timestamp'] = datetime.now().isoformat()
        
        stats = StreamAnalyzer.get_statistics(analyses)
        
        for analysis in analyses:
            analysis_history.append({
                'tweet': analysis['tweet'],
                'sentiment': analysis['sentiment'],
                'timestamp': analysis['analysis_timestamp']
            })
        
        return {
            'total_analyzed': stats['total'],
            'sentiment_distribution': stats['sentiment_distribution'],
            'average_confidence': stats['average_confidence'],
            'positive_percentage': stats['positive_percentage'],
            'negative_percentage': stats['negative_percentage'],
            'neutral_percentage': stats['neutral_percentage'],
            'analyses': analyses
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.post("/analyze/batch-with-files")
async def analyze_batch_with_files(batch: TweetBatch):
    """
    ✨ NEW! Analyze tweets AND create output files ✨
    
    This endpoint runs the full Apache Beam pipeline and creates files in output/
    
    Files created:
    - sentiment_counts_<timestamp>
    - top_hashtags_<timestamp>
    - positive_samples_<timestamp>
    - negative_samples_<timestamp>
    - detailed_analysis_<timestamp>
    """
    try:
        # Run Beam pipeline that writes files
        timestamp = run_beam_pipeline_with_files(batch.tweets)
        
        # Also get quick stats for response
        analyses = StreamAnalyzer.analyze_batch(batch.tweets)
        stats = StreamAnalyzer.get_statistics(analyses)
        
        # List created files
        output_files = glob.glob(f'output/*_{timestamp}*')
        
        return {
            'message': '✅ Analysis complete! Files created in output/ directory',
            'timestamp': timestamp,
            'statistics': stats,
            'files_created': [os.path.basename(f) for f in output_files],
            'output_directory': 'output/',
            'total_analyzed': len(batch.tweets)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis with files failed: {str(e)}")


@app.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze tweets from uploaded file (returns JSON, no files)"""
    try:
        content = await file.read()
        
        if file.filename.endswith('.txt'):
            tweets = content.decode('utf-8').strip().split('\n')
            tweets = [t.strip() for t in tweets if t.strip()]
        
        elif file.filename.endswith('.json'):
            data = json.loads(content)
            if isinstance(data, list):
                tweets = [item if isinstance(item, str) else item.get('text', '') 
                         for item in data]
            else:
                raise HTTPException(status_code=400, 
                                  detail="JSON must be an array of tweets")
        
        else:
            raise HTTPException(status_code=400, 
                              detail="Unsupported file format. Use .txt or .json")
        
        if not tweets:
            raise HTTPException(status_code=400, detail="No tweets found in file")
        
        tweets = tweets[:1000]
        
        analyses = StreamAnalyzer.analyze_batch(tweets)
        stats = StreamAnalyzer.get_statistics(analyses)
        
        hashtags = {}
        for analysis in analyses:
            tags = re.findall(r'#(\w+)', analysis['cleaned'])
            for tag in tags:
                hashtags[tag.lower()] = hashtags.get(tag.lower(), 0) + 1
        
        top_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'filename': file.filename,
            'total_tweets': len(tweets),
            'statistics': stats,
            'top_hashtags': [{'hashtag': h[0], 'count': h[1]} for h in top_hashtags],
            'sample_positive': [a for a in analyses if a['sentiment'] == 'POSITIVE'][:5],
            'sample_negative': [a for a in analyses if a['sentiment'] == 'NEGATIVE'][:5]
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


@app.post("/analyze/file-with-output")
async def analyze_file_with_output(file: UploadFile = File(...)):
    """
    ✨ NEW! Analyze uploaded file AND create output files ✨
    
    This endpoint processes the uploaded file and creates result files in output/
    """
    try:
        content = await file.read()
        
        if file.filename.endswith('.txt'):
            tweets = content.decode('utf-8').strip().split('\n')
            tweets = [t.strip() for t in tweets if t.strip()]
        elif file.filename.endswith('.json'):
            data = json.loads(content)
            if isinstance(data, list):
                tweets = [item if isinstance(item, str) else item.get('text', '') 
                         for item in data]
            else:
                raise HTTPException(status_code=400, detail="JSON must be array")
        else:
            raise HTTPException(status_code=400, detail="Use .txt or .json files")
        
        if not tweets:
            raise HTTPException(status_code=400, detail="No tweets found")
        
        tweets = tweets[:1000]
        
        # Run Beam pipeline that creates files
        timestamp = run_beam_pipeline_with_files(tweets)
        
        # Get stats for response
        analyses = StreamAnalyzer.analyze_batch(tweets)
        stats = StreamAnalyzer.get_statistics(analyses)
        
        output_files = glob.glob(f'output/*_{timestamp}*')
        
        return {
            'message': '✅ File processed! Results saved to output/ directory',
            'filename': file.filename,
            'timestamp': timestamp,
            'total_tweets': len(tweets),
            'statistics': stats,
            'files_created': [os.path.basename(f) for f in output_files],
            'output_directory': 'output/'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


@app.get("/output/files")
async def list_output_files():
    """List all files in the output directory"""
    try:
        files = glob.glob('output/*')
        
        file_info = []
        for file_path in sorted(files, key=os.path.getmtime, reverse=True):
            stat = os.stat(file_path)
            file_info.append({
                'filename': os.path.basename(file_path),
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            'output_directory': 'output/',
            'total_files': len(file_info),
            'files': file_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/statistics/overview")
async def get_statistics():
    """Get overall statistics from analysis history"""
    if not analysis_history:
        return {
            'message': 'No analyses performed yet',
            'total_analyzed': 0
        }
    
    sentiment_counts = {}
    for record in analysis_history:
        sentiment = record['sentiment']
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    return {
        'total_analyzed': len(analysis_history),
        'sentiment_distribution': sentiment_counts,
        'last_analysis': analysis_history[-1]['timestamp'] if analysis_history else None
    }


@app.get("/examples")
async def get_examples():
    """Get example tweets for testing"""
    examples = [
        "I love Apache Beam! It makes data processing so easy! 🎉 #apachebeam",
        "This is the worst documentation ever 😡 #frustrated",
        "Really enjoying learning new technologies! #tech #learning",
        "The performance is terrible. So slow! #issues",
        "Amazing community support! Thanks everyone! #opensource",
        "Successfully processed 1TB of data! #bigdata #success"
    ]
    
    return {
        'examples': examples,
        'usage': 'Use these in POST /analyze/single or /analyze/batch'
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.detail,
            'timestamp': datetime.now().isoformat()
        }
    )


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Twitter Sentiment Analysis API - Enhanced Version")
    print("="*70)
    print("📖 API Docs:       http://localhost:8000/docs")
    print("🌐 Web Interface:  Open index.html in browser")
    print("💚 Health Check:   http://localhost:8000/health")
    print("📁 Output Files:   GET /output/files (list all output files)")
    print("="*70)
    print("✨ NEW ENDPOINTS:")
    print("   POST /analyze/batch-with-files (creates output files)")
    print("   POST /analyze/file-with-output (creates output files)")
    print("="*70)
    print("📂 Output directory: ./output/")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")