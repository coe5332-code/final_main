# BSK Service Recommendation System

An AI-powered system for recommending optimal BSK (Business Service Kendra) centers for launching new services, using advanced semantic similarity and geographic intelligence.

This project implements an AI-powered training optimization system for Bangla Sahayata Kendras (BSKs), designed to provide personalized, adaptive training for operators and intelligent service recommendations.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12 or higher
- PostgreSQL database with BSK data
- 8GB+ RAM (for AI models)

### 2. Installation

```bash
# Clone and navigate to project
cd project-folder

# Install dependencies
pip install -r requirements.txt

# Alternative: Install from environment.yml
conda env create -f environment.yml
conda activate bskwebel
```

### 3. Database Setup

1. Configure your database connection in `backend/app/models/database.py`
2. Ensure your database contains the required tables:
   - `ml_bsk_master` (BSK centers)
   - `ml_service_master` (services)
   - `ml_provision` (service provisions)
   - `ml_deo_master` (DEO agents)

### 4. Start the System

#### Run system diagnostics first
```bash
python check_system.py
```

#### Start backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 54300
```

#### Start frontend (in new terminal)
```bash
streamlit run app.py
```

## 🛠️ System Architecture

### Key Features
- 🤖 **AI-Powered Matching**: Uses sentence transformers for semantic similarity
- 📊 **Usage Analytics**: Historical service provision analysis
- 🗺️ **Geographic Intelligence**: Location-based recommendations
- 🔍 **Advanced Filtering**: Multi-dimensional filtering options
- 📈 **Interactive Visualizations**: Maps, charts, and analytics
- ⚡ **Performance Optimized**: Precomputed embeddings and clustering

## 🔧 Troubleshooting

### Common Issues

**"Database service not available"**
- Ensure PostgreSQL is running and accessible
- Check database connection string in `backend/app/models/database.py`
- Verify required tables exist

**"AI model loading failed"**
- Install PyTorch: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
- Ensure sufficient RAM (8GB+)

**"Backend API not accessible"**
- Start backend: `cd backend && python -m uvicorn app.main:app --reload --port 54300`
- Check port 54300 is available

**"Embeddings initialization failed"**
- Install ChromaDB: `pip install chromadb`
- Check disk space for vector storage

## Project Structure

```
webel-urgent/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   └── schemas/        # Pydantic schemas
│   └── tests/              # Backend tests
├── frontend/               # Streamlit frontend
│   ├── pages/             # Streamlit pages
│   ├── components/        # Reusable components
│   └── utils/             # Frontend utilities
├── ai_service/            # AI/ML service
│   ├── models/            # ML models
│   ├── training/          # Training scripts
│   └── utils/             # AI utilities
└── docs/                  # Documentation
```

## Setup Instructions

### Prerequisites
- Python 3.12+ (recommended: 3.13)
- Miniconda or Anaconda

### Option 1: Using Conda (Recommended)

1. Install Miniconda (if not already installed):
   - Download from: https://docs.conda.io/en/latest/miniconda.html
   - Follow the installation instructions for your operating system

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate bskwebel
```

3. Verify installation:
```bash
python check_dependencies.py
```

### Option 2: Using pip

1. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r frontend/requirements.txt
```

### Environment Setup

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
DATABASE_URL=your-db-urlk
SECRET_KEY=your-secret-key
```

### Running the Application

4. Start the services:

Backend:
```bash
cd backend
python run.py
```
The backend will be available at: http://localhost:54300

Frontend:
```bash
cd frontend
streamlit run app.py
```
The frontend will be available at: http://localhost:8501

### Service Recommendation Page
To access the AI-powered service recommendation system:
```bash
cd frontend
streamlit run pages/05_Service_Recommendation.py
```

## Troubleshooting

### Import Errors
If you encounter import errors like "cannot import name 'recommend_bsk_for_service_from_db'":

1. Check dependencies:
```bash
python check_dependencies.py
```

2. Reinstall missing packages:
```bash
pip install sentence-transformers chromadb geopy nltk
```

3. If AI features are not available, the system will automatically fall back to API-based recommendations.

### Database Connection Issues
- Ensure the DATABASE_URL in your .env file is correct
- Check if the backend service is running on port 54300
- Verify network connectivity to the Neon database

### Common Solutions
- **Memory Issues**: ChromaDB embeddings require sufficient RAM. If you encounter memory errors, try using smaller datasets or disable AI embeddings.
- **Port Conflicts**: If ports 54300 or 8501 are in use, modify the port numbers in the configuration files.
- **Permission Errors**: On Windows, you may need to run the terminal as administrator for some installations.



## Features

### AI-Powered Service Recommendation System
The system now includes advanced AI capabilities for BSK recommendations:

- **Semantic Similarity Matching**: Uses sentence transformers to understand service descriptions
- **ChromaDB Integration**: Efficient storage and retrieval of service embeddings
- **Geographic Analysis**: Location-based recommendations with proximity scoring
- **Interactive Dashboard**: Advanced filtering, analytics, and visualizations
- **Fallback Mode**: Automatic fallback to traditional methods if AI is unavailable

### Core Functionality
- BSK performance analysis and recommendations
- Service optimization suggestions
- Geographic distribution analysis
- Export capabilities for further analysis

## Database Schema

The system uses the following main tables:
- BSK Master
- Service Master
- Department Master
- DEO Master
- Citizen Master
- District Master
- Transaction Tables

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## License

This project is proprietary and confidential and only to be used by Webel

Built by Rishi Paul,Suvam Manna,Debargha Biswas