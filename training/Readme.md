# 🎓 BSK Training Optimization System

> **AI-Powered Training Management & Video Generation Platform for Bank Sathi Kendra**

A comprehensive system for managing, optimizing, and delivering training content to Bank Sathi Kendra (BSK) centers and Data Entry Operators (DEOs) across districts.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

The BSK Training Optimization System is an end-to-end platform that:

- **Manages** BSK centers, DEOs, services, and provisions data
- **Analyzes** performance using AI/ML algorithms
- **Recommends** optimal BSKs for new service launches
- **Identifies** underperforming centers requiring training
- **Generates** professional training videos automatically
- **Tracks** training video lifecycle and coverage metrics

### Key Capabilities

- 🤖 **AI-Powered Recommendations** - Service-BSK matching using embeddings
- 📊 **Performance Analytics** - K-means clustering and gap analysis
- 🎥 **Automated Video Generation** - PDF/Form → Training Video pipeline
- 📈 **MIS Dashboard** - Real-time monitoring and alerts
- 🗺️ **Geographic Analysis** - Interactive maps with PyDeck

---

## ✨ Features

### 1. Data Management
- View and manage BSK centers, services, DEOs, and provisions
- Advanced filtering and search capabilities
- Interactive charts and visualizations
- CSV export functionality

### 2. AI-Powered Analytics

#### **Service Recommendation Engine**
- Finds optimal BSKs for launching new services
- Uses semantic similarity (ChromaDB embeddings)
- Geographic clustering for better targeting
- Configurable ranking algorithms

#### **Underperforming BSK Detection**
- Identifies centers needing support
- Multi-dimensional performance scoring
- Cluster benchmarking
- District-wise analysis

#### **Training Need Identification**
- Service gap analysis per BSK
- Priority scoring system
- DEO-level training assignments
- Exportable action plans

### 3. Training Video Generation

- **PDF to Video**: Convert training PDFs to narrated videos
- **Form-based Creation**: Build videos from structured content
- **Video Upload**: Manage existing video content
- **Version Control**: Track multiple versions per service
- **AI Narration**: Text-to-speech in multiple Indian voices
- **Smart Slides**: Gemini AI generates optimal slide structure
- **Visual Assets**: Automatic image sourcing from Unsplash

### 4. MIS Dashboard

- Executive summary with key metrics
- Video lifecycle management
- Coverage analytics
- Alert system for missing/outdated content
- Action item tracking

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - High-performance REST API
- **SQLAlchemy** - ORM for database management
- **Pandas** - Data processing and analytics
- **Scikit-learn** - Machine learning (K-means clustering)
- **ChromaDB** - Vector database for embeddings
- **Python-dotenv** - Environment configuration

### AI/ML Services
- **Google Gemini AI** - Slide content generation
- **Azure TTS** - Text-to-speech synthesis
- **ChromaDB** - Semantic search with embeddings

### Frontend
- **Streamlit** - Interactive web interface
- **Plotly** - Advanced data visualizations
- **PyDeck** - Geographic mapping
- **Pandas** - Data manipulation

### Video Processing
- **MoviePy** - Video composition and editing
- **Pillow (PIL)** - Image processing
- **PyPDF2 / pdfplumber** - PDF content extraction
- **ReportLab** - PDF generation

### External APIs
- **Unsplash API** - Stock photography
- **Azure Cognitive Services** - Speech synthesis

---

## 📁 Project Structure

```
bsk-training-system/
│
├── ai_service/              # AI/ML analytics modules
│   ├── bsk_analytics.py     # Underperforming BSK detection
│   ├── service_recommendation.py  # Service-BSK matching
│   └── database_service.py  # Direct DB access helpers
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models/
│   │   │   ├── models.py    # SQLAlchemy ORM models
│   │   │   ├── schemas.py   # Pydantic schemas
│   │   │   └── database.py  # Database connection
│   │   └── main.py          # FastAPI app & endpoints
│   └── .env                 # Environment variables
│
├── deos_training/           # Training recommendation module
│   └── training_recommendation.py
│
├── frontend/                # Streamlit web interface
│   ├── pages/
│   │   ├── 01_BSK_Centers.py
│   │   ├── 02_Services.py
│   │   ├── 03_DEOs.py
│   │   ├── 04_Provisions.py
│   │   ├── 05_Service_Recommendation.py
│   │   ├── 06_Underperforming_BSKs.py
│   │   ├── 07_Training_Recommendations.py
│   │   ├── 08_Training_Video_Generator.py
│   │   └── 09_MIS_Dashboard.py
│   ├── app.py               # Main Streamlit app
│   └── page_utils.py        # Shared utilities
│
├── services/                # External service integrations
│   ├── gemini_service.py    # Google Gemini AI
│   └── unsplash_service.py  # Unsplash image API
│
├── utils/                   # Utility functions
│   ├── audio_utils.py       # Text-to-speech
│   ├── video_utils.py       # Video composition
│   ├── avatar_utils.py      # Avatar overlay
│   ├── pdf_extractor.py     # PDF content extraction
│   ├── pdf_utils.py         # PDF generation
│   └── service_utils.py     # Validation helpers
│
├── videos/                  # Generated video storage
│   └── {service_id}/
│       └── {service_name}_v{version}.mp4
│
├── chroma_db/               # ChromaDB vector store
├── images/                  # Cached Unsplash images
├── generated_pdfs/          # Generated training PDFs
├── assets/                  # Static assets
│
├── README.md                # This file
├── SETUP.md                 # Setup instructions
└── requirements.txt         # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- SQL Server database
- API keys (Google Gemini, Unsplash, Azure)
- ImageMagick (for video generation)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd bsk-training-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp backend/.env.example backend/.env
# Edit .env with your credentials

# 4. Initialize database
cd backend
python -c "from app.models.database import engine; from app.models import models; models.Base.metadata.create_all(bind=engine)"

# 5. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 54300 --reload

# 6. Start frontend (new terminal)
cd ../frontend
streamlit run app.py
```

**Access the application:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:54300
- API Docs: http://localhost:54300/docs

See [SETUP.md](SETUP.md) for detailed instructions.

---

## 📖 Usage Guide

### 1. Data Management

Navigate through pages 01-04 to view and analyze:
- BSK Centers (locations, types, status)
- Services (catalog, departments)
- DEOs (assignments, contact info)
- Provisions (transactions, usage)

**Features:**
- Pagination controls (limit/skip)
- Interactive charts (Plotly)
- CSV export
- Advanced filtering

### 2. Service Recommendations (Page 05)

**Find optimal BSKs for new services:**

1. Enter service details (name, type, description)
2. Configure options:
   - Use embeddings (faster, requires initialization)
   - Number of recommendations
   - Include inactive BSKs
3. Click "Get Recommendations"

**Results include:**
- Top BSKs ranked by score
- Recommendation reasons
- Similar existing services
- Geographic distribution map
- Exportable results

### 3. Underperforming BSKs (Page 06)

**Identify centers needing attention:**

1. Set analysis parameters (date range, number of BSKs)
2. Choose sorting (lowest/highest score)
3. Apply filters (district, block, BSK name)

**View:**
- Performance scores
- Cluster analysis
- Geographic distribution
- Recommended training services
- DEO assignments

### 4. Training Recommendations (Page 07)

**Prioritize training needs:**

1. System fetches recommendations automatically
2. Filter by:
   - District
   - BSK type
   - Priority score threshold
3. Explore tabs:
   - BSK Details (individual center view)
   - District Analysis
   - Service Analysis
   - Geographic View
   - Export options

### 5. Video Generation (Page 08)

**Create training videos:**

#### Option A: PDF Upload
1. Select service
2. Choose "Upload PDF"
3. Upload training document
4. Select narrator voice
5. Generate video

#### Option B: Form Entry
1. Select service
2. Choose "Manual Form Entry"
3. Fill in:
   - Service description
   - Application process
   - Eligibility criteria
   - Required documents
   - Operator tips
   - Troubleshooting
4. Select narrator voice
5. Generate video

#### Option C: Video Upload
1. Select service
2. Choose "Upload Existing Video"
3. Upload MP4/MOV/AVI file
4. System manages versioning automatically

**Video Features:**
- Automatic versioning (v1, v2, v3...)
- Database record creation
- Multi-language narrator options
- AI-generated slides (Gemini)
- Professional animations
- Avatar overlay

### 6. MIS Dashboard (Page 09)

**Monitor system health:**

- **Executive Summary**: Key metrics, coverage stats
- **Video Lifecycle**: Creation timeline, version management
- **Analytics**: Department-wise coverage, storage usage
- **Alerts**: Missing videos, outdated content, high-priority needs

---

## 📡 API Documentation

### Core Endpoints

#### BSK Centers
```
GET  /bsk/              # List BSKs (paginated)
GET  /bsk/{bsk_id}      # Get specific BSK
```

#### Services
```
GET  /services/              # List services
GET  /services/{service_id}  # Get service details
```

#### DEOs
```
GET  /deo/              # List DEOs
GET  /deo/{agent_id}    # Get DEO details
```

#### Provisions
```
GET  /provisions/              # List provisions
GET  /provisions/{customer_id} # Get provision
```

#### Analytics
```
GET  /underperforming_bsks/
  ?num_bsks=50
  &sort_order=asc

GET  /service_training_recomendation/
  ?limit=100
  &summary_only=false
```

#### Service Videos
```
POST   /service_videos/           # Create/update record
GET    /service_videos/{service_id}
PUT    /service_videos/{service_id}
PATCH  /service_videos/{service_id}/mark_old
```

**Full API documentation**: http://localhost:54300/docs

---

## 🔧 Configuration

### Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server

# Google Gemini AI
GOOGLE_API_KEY=your_google_api_key

# Unsplash
UNSPLASH_ACCESS_KEY=your_unsplash_access_key

# Azure Text-to-Speech
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=your_region

# Video Settings
IMAGEMAGICK_BINARY=C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe
```

### ImageMagick Setup

**Windows:**
```bash
# Download from: https://imagemagick.org/script/download.php
# Install with "Install legacy utilities (e.g. convert)" checked
```

**Linux:**
```bash
sudo apt-get install imagemagick
```

**Mac:**
```bash
brew install imagemagick
```

Update path in `utils/video_utils.py` if needed.

---

## 📊 Data Models

### Core Tables

- **BSKMaster**: BSK center information
- **ServiceMaster**: Service catalog
- **DEOMaster**: Data entry operator records
- **Provision**: Service transaction records
- **ServiceVideo**: Video metadata and versioning

See `backend/app/models/models.py` for complete schema.

---

## 🎯 Key Algorithms

### 1. Service Recommendation
- **Method**: Semantic similarity using ChromaDB embeddings
- **Features**: Service description, type, department
- **Ranking**: Cosine similarity + usage count + geographic proximity

### 2. Underperforming BSK Detection
- **Method**: K-means clustering on geographic coordinates
- **Metrics**: Provision volume, service diversity, efficiency
- **Scoring**: Composite score vs. cluster average

### 3. Training Need Identification
- **Method**: Cluster benchmarking + gap analysis
- **Process**: 
  1. Cluster BSKs geographically
  2. Identify top services per cluster
  3. Find BSKs below cluster average
  4. Generate prioritized recommendations

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Fails**
```
Solution: Verify DATABASE_URL in .env
Check ODBC driver installation
Test connection: python -c "from app.models.database import engine; engine.connect()"
```

**2. Video Generation Errors**
```
Solution: Ensure ImageMagick is installed
Verify IMAGEMAGICK_BINARY path
Check API keys (GOOGLE_API_KEY, AZURE_TTS_KEY)
```

**3. Embeddings Not Working**
```
Solution: Initialize embeddings on first use
Run: python -m ai_service.service_recommendation
Check ChromaDB directory permissions
```

**4. API Timeout**
```
Solution: Increase timeout in requests
For large datasets, use summary_only=True
Consider database indexing
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to functions
- Update tests for new features
- Document API changes

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Team & Support

**Developed by**: BSK Training System Team

**For Support:**
- Email: support@bsk-training.example
- Issues: GitHub Issues
- Documentation: [Wiki](wiki-url)

---

## 🙏 Acknowledgments

- Google Gemini AI for content generation
- Unsplash for training imagery
- Azure Cognitive Services for TTS
- Streamlit community for excellent framework

---

## 🗺️ Roadmap

### Upcoming Features

- [ ] Multi-language video generation
- [ ] Advanced analytics (predictive modeling)
- [ ] Mobile app integration
- [ ] Automated video quality assessment
- [ ] Real-time training tracking
- [ ] Integration with LMS platforms

---
