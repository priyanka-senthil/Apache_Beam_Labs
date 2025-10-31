# 🐦 Twitter Sentiment Analysis API

A production-ready REST API for real-time sentiment analysis of tweets, powered by **Apache Beam** and **FastAPI**.

---

## ✨ Features

- **🔍 Real-time Sentiment Analysis** - Analyze tweets instantly with confidence scores
- **📊 Batch Processing** - Process up to 1000 tweets at once
- **📁 File Upload Support** - Upload `.txt` or `.json` files for bulk analysis
- **🧠 Advanced NLP**
  - Negation handling ("not good" → negative)
  - Emoji sentiment detection 😊😡
  - Confidence scoring (0-100%)
  - Multi-word expression analysis
- **📈 Analytics Dashboard** - Track analysis history and statistics
- **🌐 Interactive UI** - Beautiful web interface included
- **📖 Auto-generated Docs** - Swagger UI and ReDoc

---

## 🎬 Demo

### Web Interface
![Web Interface Screenshot](https://via.placeholder.com/800x400/667eea/ffffff?text=Beautiful+Web+Interface)

### API Documentation
![Swagger UI Screenshot](https://via.placeholder.com/800x400/764ba2/ffffff?text=Interactive+API+Docs)

### Analysis Results
![Results Screenshot](https://via.placeholder.com/800x400/38ef7d/ffffff?text=Detailed+Sentiment+Analysis)

---

## 💻 Installation

### Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### Step-by-Step Setup

#### 1️⃣ Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Apache_Beam_Labs

# Or download and extract the ZIP file
```

#### 2️⃣ Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv apache_lab
source apache_lab/bin/activate

# On Windows
python -m venv apache_lab
apache_lab\Scripts\activate
```

You should see `(apache_lab)` in your terminal prompt.

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed apache-beam-2.69.0 fastapi-0.115.0 uvicorn-0.32.0 ...
```

#### 4️⃣ Verify Installation

```bash
python -c "import fastapi; import apache_beam; print('✅ All dependencies installed!')"
```

---

## 🚀 Quick Start

### Start the API Server

```bash
python main.py
```

**Expected output:**
```
🚀 Starting Twitter Sentiment Analysis API...
📖 Documentation: http://localhost:8000/docs
🌐 HTML Interface: Open index.html in your browser
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Access the Application

1. **Web Interface**: Open `index.html` in your browser
2. **API Docs**: Visit http://localhost:8000/docs
3. **API Endpoint**: http://localhost:8000

---

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/analyze/single` | Analyze one tweet |
| POST | `/analyze/batch` | Analyze multiple tweets |
| POST | `/analyze/file` | Upload file for analysis |
| GET | `/statistics/overview` | Get overall statistics |
| GET | `/statistics/recent/{limit}` | Get recent analyses |
| DELETE | `/statistics/clear` | Clear history |
| GET | `/examples` | Get example tweets |

---

## 📝 Usage Examples

### 1️⃣ Analyze Single Tweet

#### Using Web Interface
1. Open `index.html` in browser
2. Enter tweet text
3. Click "🔍 Analyze Tweet"
4. View results instantly!

![Single Tweet Analysis](https://via.placeholder.com/700x300/667eea/ffffff?text=Step+1%3A+Enter+Tweet)

#### Using cURL
```bash
curl -X POST "http://localhost:8000/analyze/single" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I absolutely love Apache Beam! Best tool ever! 🎉"
  }'
```

#### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze/single",
    json={"text": "I love Apache Beam! 🎉"}
)

result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']}")
```

**Response:**
```json
{
  "tweet": "I absolutely love Apache Beam! Best tool ever! 🎉",
  "sentiment": "POSITIVE",
  "confidence": 0.857,
  "positive_score": 6,
  "negative_score": 0,
  "emoji_score": 2,
  "analysis_timestamp": "2025-10-31T12:00:00"
}
```

---

### 2️⃣ Batch Analysis

Process multiple tweets at once (up to 1000):

```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "tweets": [
      "I love this! 😊",
      "This is terrible 😡",
      "Apache Beam rocks!",
      "Worst experience ever",
      "Amazing tool! 🎉"
    ]
  }'
```

**Response:**
```json
{
  "total_analyzed": 5,
  "sentiment_distribution": {
    "POSITIVE": 3,
    "NEGATIVE": 2
  },
  "average_confidence": 0.78,
  "positive_percentage": 60.0,
  "negative_percentage": 40.0,
  "analyses": [...]
}
```

---

### 3️⃣ File Upload

Upload a text file with one tweet per line:

#### Create sample file
```bash
cat > tweets.txt << EOF
I love Apache Beam! 🎉
This is terrible 😡
Great documentation!
Horrible experience
Amazing tool!
EOF
```

#### Upload via cURL
```bash
curl -X POST "http://localhost:8000/analyze/file" \
  -F "file=@tweets.txt"
```

#### Upload via Python
```python
with open('tweets.txt', 'rb') as f:
    response = requests.post(
        "http://localhost:8000/analyze/file",
        files={'file': ('tweets.txt', f, 'text/plain')}
    )
print(response.json())
```

---

### 4️⃣ Get Statistics

```bash
curl http://localhost:8000/statistics/overview
```

**Response:**
```json
{
  "total_analyzed": 150,
  "sentiment_distribution": {
    "POSITIVE": 75,
    "NEGATIVE": 50,
    "NEUTRAL": 25
  },
  "last_analysis": "2025-10-31T12:00:00"
}
```

---

## 📁 Project Structure

```
Apache_Beam_Labs/
│
├── main.py                    # FastAPI application (main server)
├── sentiment_analyzer.py      # Core sentiment analysis logic
├── beam_pipeline.py           # Apache Beam pipeline utilities
├── index.html                 # Web interface
├── requirements.txt           # Python dependencies
├── test_api.py               # Automated test suite
├── README.md                 # This file
│
├── apache_lab/               # Virtual environment (created during setup)
│   └── ...
│
└── output/                   # Analysis results (auto-created)
    ├── sentiment_counts-*
    ├── top_hashtags-*
    └── ...
```

---

## 🔬 How It Works

### Architecture Overview

```
┌─────────────┐
│   Client    │ (Browser/App/cURL/Python)
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  ┌──────────────────────────────┐  │
│  │  Endpoints:                  │  │
│  │  • /analyze/single           │  │
│  │  • /analyze/batch            │  │
│  │  • /analyze/file             │  │
│  │  • /statistics/*             │  │
│  └──────────────────────────────┘  │
└───────────┬─────────────────────────┘
            │
            ↓
┌───────────────────────────────────┐
│    Sentiment Analyzer Module      │
│  ┌─────────────────────────────┐ │
│  │ • Text cleaning             │ │
│  │ • Word tokenization         │ │
│  │ • Negation handling         │ │
│  │ • Emoji analysis            │ │
│  │ • Confidence calculation    │ │
│  └─────────────────────────────┘ │
└───────────┬───────────────────────┘
            │
            ↓
┌───────────────────────────────────┐
│       Sentiment Result            │
│  • Sentiment (POS/NEG/NEU)        │
│  • Confidence score (0-1)         │
│  • Positive/Negative scores       │
│  • Emoji impact                   │
│  • Timestamp                      │
└───────────────────────────────────┘
```

### Sentiment Analysis Algorithm

1. **Text Preprocessing**
   - Convert to lowercase
   - Remove URLs
   - Extract words

2. **Word Analysis**
   - Match against positive word dictionary
   - Match against negative word dictionary
   - Handle negations ("not good" → negative)

3. **Emoji Analysis**
   - Detect positive emojis (😊🎉❤️)
   - Detect negative emojis (😡😢💔)
   - Weight emojis 2x more than words

4. **Score Calculation**
   ```
   Positive Score = Positive Words + Positive Emojis
   Negative Score = Negative Words + Negative Emojis
   
   If Positive > Negative → POSITIVE
   If Negative > Positive → NEGATIVE
   Else → NEUTRAL
   
   Confidence = Max Score / (Total Score + 1)
   ```

---

## 🧪 Testing

### Run Automated Tests

```bash
python test_api.py
```

**Expected output:**
```
============================================================
Testing Health Check
============================================================
Status Code: 200
Response: {
  "status": "healthy",
  "version": "1.0.0"
}

============================================================
Testing Single Tweet Analysis
============================================================
Status Code: 200
Tweet: I absolutely love Apache Beam!
Sentiment: POSITIVE
Confidence: 0.857
...
```

### Manual Testing via Swagger UI

1. Open http://localhost:8000/docs
2. Click on any endpoint (e.g., `POST /analyze/single`)
3. Click **"Try it out"**
4. Enter test data:
   ```json
   {
     "text": "I love Apache Beam! 🎉"
   }
   ```
5. Click **"Execute"**
6. View the response!

![Swagger UI Testing](https://via.placeholder.com/700x300/764ba2/ffffff?text=Swagger+UI+Testing)

---

## 🐛 Troubleshooting

### Problem 1: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'sentiment_analyzer'
```

**Solution:**
Make sure all three files exist in the same directory:
- `main.py`
- `sentiment_analyzer.py`
- `beam_pipeline.py`

```bash
ls -la *.py
```

---

### Problem 2: CORS Error (Failed to fetch)

**Error in browser:**
```
Failed to fetch
Access to fetch has been blocked by CORS policy
```

**Solution:**
Make sure your `main.py` has CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Problem 3: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or change port in main.py:
uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

### Problem 5: Virtual Environment Not Activated

**Symptom:** Packages not found even after installation

**Solution:**
```bash
# Activate virtual environment
# On macOS/Linux:
source apache_lab/bin/activate

# On Windows:
apache_lab\Scripts\activate

# Verify activation (should show (apache_lab)):
which python
```

---
