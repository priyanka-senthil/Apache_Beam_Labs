# 🐦 Twitter Sentiment Analysis with Apache Beam & FastAPI

A real-time sentiment analysis API that analyzes tweets using Apache Beam for data processing and FastAPI for the REST API.

---

## 📋 Project Overview

This project demonstrates **Apache Beam** concepts through a practical sentiment analysis application. It processes tweets to determine if they're positive, negative, or neutral using:

- **Apache Beam:** For distributed data processing
- **FastAPI:** For REST API endpoints
- **NLP Techniques:** Negation handling, emoji analysis, confidence scoring

---

## 🎯 What We Built

### **1. Core Features**
- ✅ Single tweet sentiment analysis
- ✅ Batch processing (up to 1000 tweets)
- ✅ File upload support (.txt, .json)
- ✅ Real-time analysis with confidence scores
- ✅ Hashtag and mention extraction

### **2. Advanced Sentiment Analysis**
- Positive/negative word detection
- Negation handling ("not good" → negative)
- Emoji sentiment analysis (😊 🎉 😡 😢)
- Confidence scoring (0-100%)

### **3. API Endpoints**
```
POST /analyze/single              # Analyze one tweet
POST /analyze/batch               # Analyze multiple tweets
POST /analyze/batch-with-files    # Batch + create output files
POST /analyze/file                # Upload file
POST /analyze/file-with-output    # Upload + create output files
GET  /output/files                # List output files
GET  /docs                        # Interactive API docs
```

### **4. Web Interface**
- Beautiful responsive UI
- Three tabs: Single, Batch, File Upload
- Real-time results visualization
- Drag & drop file upload

---

## 🔧 Modifications from Word Count Example

| **Word Count Lab** | **Our Sentiment Analysis Project** |
|-------------------|-----------------------------------|
| Count word frequency | Analyze tweet sentiment |
| Single input file | Multiple input methods (text, batch, file) |
| Basic Map/FlatMap | Advanced NLP with negation handling |
| Text output only | JSON API responses + optional file output |
| Command-line only | Web UI + REST API |
| Simple pipeline | Multiple pipelines with statistics |
| No real-time processing | Real-time API responses |
| ReadFromText → Count → Write | Read → Analyze → Extract → Aggregate → Multiple outputs |

### **Key Apache Beam Concepts Added:**
- ✅ `beam.Filter` for filtering by sentiment
- ✅ `beam.ParDo` for custom transformations
- ✅ `beam.CombinePerKey` for aggregations
- ✅ `beam.combiners.Top.Of` for rankings
- ✅ `beam.combiners.Sample` for sampling
- ✅ Multiple parallel pipelines in one run
- ✅ Integration with FastAPI for web serving

---

## 📁 Project Structure

```
Apache_Beam_Labs/
│
├── main.py                    # FastAPI application (REST API server)
├── sentiment_analyzer.py      # Core sentiment analysis logic
├── beam_pipeline.py          # Apache Beam pipeline utilities
├── index.html                # Web interface (3 tabs: Single/Batch/File)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── output/                   # Output files (created when using *-with-files endpoints)
│   ├── sentiment_counts_*
│   ├── top_hashtags_*
│   ├── positive_samples_*
│   ├── negative_samples_*
│   └── detailed_analysis_*
│
└── apache_lab/              # Virtual environment (created during setup)
```

---

## 🚀 How to Run

### **Prerequisites**
- Python 3.9+
- pip

### **Step 1: Setup**
```bash
# Create virtual environment
python3 -m venv apache_lab
source apache_lab/bin/activate  # Windows: apache_lab\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Start Server**
```bash
python main.py
```

**Expected output:**
```
======================================================================
🚀 Twitter Sentiment Analysis API - Enhanced Version
======================================================================
📖 API Docs:       http://localhost:8000/docs
🌐 Web Interface:  Open index.html in browser
💚 Health Check:   http://localhost:8000/health
📁 Output Files:   GET /output/files
======================================================================
```

### **Step 3: Use the Application**

#### **Option A: Web Interface** (Easiest)
1. Open `index.html` in your browser
2. Choose a tab (Single/Batch/File)
3. Enter or upload tweets
4. Click analyze!

#### **Option B: API with cURL**
```bash
# Analyze single tweet
curl -X POST "http://localhost:8000/analyze/single" \
  -H "Content-Type: application/json" \
  -d '{"text":"I love Apache Beam! 🎉"}'

# Batch analysis (creates files in output/)
curl -X POST "http://localhost:8000/analyze/batch-with-files" \
  -H "Content-Type: application/json" \
  -d '{"tweets":["Tweet 1","Tweet 2","Tweet 3"]}'

# View output files
ls -la output/
cat output/sentiment_counts_*
```

#### **Option C: Interactive Swagger UI**
Visit: http://localhost:8000/docs

---

## 📊 Example Usage

### **Input:**
```
"I love Apache Beam! It's amazing! 🎉 #apachebeam"
```

### **Output:**
```json
{
  "tweet": "I love Apache Beam! It's amazing! 🎉 #apachebeam",
  "sentiment": "POSITIVE",
  "confidence": 0.857,
  "positive_score": 6,
  "negative_score": 0,
  "emoji_score": 2
}
```

---

## 🎓 Learning Outcomes

### **Apache Beam Concepts Learned:**
- Pipeline creation and execution
- PCollections and transformations
- Map, FlatMap, Filter operations
- CombinePerKey for aggregations
- ParDo for custom processing
- Writing to multiple outputs
- Sampling and ranking data

### **MLOps Concepts:**
- Building production APIs
- Real-time data processing
- Batch vs streaming patterns
- API design and documentation
- Error handling and validation

---

## 🛠️ Tech Stack

- **Apache Beam 2.69.0** - Data processing framework
- **FastAPI 0.115.0** - Modern Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

---

## 📝 Quick Commands

```bash
# Start server
python main.py

# Test API
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Check output files
ls -la output/

# Stop server
CTRL + C
```

---

## ✨ Key Features Summary

| Feature | Description |
|---------|-------------|
| 🔍 Real-time Analysis | Instant sentiment detection |
| 📊 Batch Processing | Handle 1000+ tweets at once |
| 📁 File Upload | Support for .txt and .json |
| 🎯 High Accuracy | Advanced NLP with negation handling |
| 😊 Emoji Support | Detects emoji sentiment |
| 📈 Confidence Scores | 0-100% confidence rating |
| 🌐 Web Interface | Beautiful, responsive UI |
| 📖 Auto Documentation | Swagger UI included |
| 📂 File Output | Optional output files for analysis |

---

**Built with ❤️ for MLOps Course**

Apache Beam + FastAPI = Powerful Data Processing API 🚀