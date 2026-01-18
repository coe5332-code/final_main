# 🔧 BSK Training System - Complete Setup Guide

This guide provides step-by-step instructions for setting up the BSK Training Optimization System on your local machine or server.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [External Services Setup](#external-services-setup)
7. [Running the Application](#running-the-application)
8. [Verification & Testing](#verification--testing)
9. [Production Deployment](#production-deployment)
10. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software

- **Python 3.9 or higher**
  ```bash
  python --version  # Should show 3.9+
  ```

- **pip (Python package manager)**
  ```bash
  pip --version
  ```

- **Git**
  ```bash
  git --version
  ```

- **Microsoft SQL Server** (or compatible database)
  - SQL Server 2017+ recommended
  - OR Azure SQL Database

- **ODBC Driver for SQL Server**
  - [Download ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

- **ImageMagick** (for video generation)
  - [Download ImageMagick](https://imagemagick.org/script/download.php)

### Required API Keys

You'll need accounts and API keys for:

1. **Google Gemini AI** - For slide generation
   - Get key: https://ai.google.dev/
   
2. **Unsplash** - For training images
   - Get key: https://unsplash.com/developers
   
3. **Azure Cognitive Services** - For text-to-speech
   - Get key: https://azure.microsoft.com/en-us/services/cognitive-services/

---

## 2. System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 11+
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **Network**: Stable internet connection

### Recommended Requirements

- **CPU**: 8+ cores
- **RAM**: 16 GB+
- **Storage**: 50 GB SSD
- **GPU**: Optional, for faster video processing

---

## 3. Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd bsk-training-system

# Verify directory structure
ls -la
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

**Key packages to verify:**
- fastapi
- streamlit
- sqlalchemy
- pandas
- scikit-learn
- chromadb
- moviepy
- Pillow
- google-generativeai
- azure-cognitiveservices-speech

### Step 4: Install ImageMagick

#### Windows:
1. Download installer from https://imagemagick.org/script/download.php
2. During installation, **check "Install legacy utilities (e.g. convert)"**
3. Add to PATH (usually automatic)
4. Verify:
   ```bash
   magick --version
   ```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install imagemagick
convert --version
```

#### macOS:
```bash
brew install imagemagick
convert --version
```

### Step 5: Install ODBC Driver

#### Windows:
1. Download [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Run installer
3. Verify in ODBC Data Sources (64-bit)

#### Linux:
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

#### macOS:
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17
```

---

## 4. Database Setup

### Step 1: Create Database

Connect to your SQL Server and run:

```sql
-- Create database
CREATE DATABASE BSKTrainingDB;
GO

-- Create schema
USE BSKTrainingDB;
GO

CREATE SCHEMA dbo;
GO
```

### Step 2: Create Database User (Optional)

```sql
-- Create login
CREATE LOGIN bsk_user WITH PASSWORD = 'YourSecurePassword123!';
GO

-- Create user and grant permissions
USE BSKTrainingDB;
GO

CREATE USER bsk_user FOR LOGIN bsk_user;
GO

ALTER ROLE db_datareader ADD MEMBER bsk_user;
ALTER ROLE db_datawriter ADD MEMBER bsk_user;
ALTER ROLE db_ddladmin ADD MEMBER bsk_user;
GO
```

### Step 3: Initialize Tables

The application will create tables automatically on first run, but you can manually initialize:

```bash
cd backend
python -c "from app.models.database import engine; from app.models import models; models.Base.metadata.create_all(bind=engine)"
```

### Step 4: Load Sample Data (Optional)

If you have sample data:

```sql
-- Insert sample BSK
INSERT INTO dbo.ml_bsk_master (bsk_id, bsk_name, bsk_code, district_name, is_active)
VALUES (1, 'Sample BSK Center', 'BSK001', 'Sample District', 1);

-- Insert sample service
INSERT INTO dbo.ml_service_master (service_id, service_name, service_type, is_active)
VALUES (1, 'Sample Service', 'G', 1);
```

---

## 5. Environment Configuration

### Step 1: Create Environment File

```bash
cd backend
cp .env.example .env
# OR
touch .env
```

### Step 2: Configure .env File

Edit `backend/.env` with your settings:

```env
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=mssql+pyodbc://username:password@server_address/database_name?driver=ODBC+Driver+17+for+SQL+Server

# Example (local):
# DATABASE_URL=mssql+pyodbc://sa:YourPassword123!@localhost/BSKTrainingDB?driver=ODBC+Driver+17+for+SQL+Server

# Example (Azure SQL):
# DATABASE_URL=mssql+pyodbc://username@servername:password@servername.database.windows.net/BSKTrainingDB?driver=ODBC+Driver+17+for+SQL+Server


# ============================================
# GOOGLE GEMINI AI
# ============================================
GOOGLE_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash


# ============================================
# UNSPLASH API
# ============================================
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
UNSPLASH_API_URL=https://api.unsplash.com/search/photos


# ============================================
# AZURE COGNITIVE SERVICES (Text-to-Speech)
# ============================================
AZURE_TTS_KEY=your_azure_tts_subscription_key
AZURE_TTS_REGION=your_azure_region
# Example: AZURE_TTS_REGION=eastus


# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=development
DEBUG=True
API_BASE_URL=http://localhost:54300


# ============================================
# VIDEO GENERATION SETTINGS
# ============================================
# Windows path example:
IMAGEMAGICK_BINARY=C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe

# Linux/Mac path example:
# IMAGEMAGICK_BINARY=/usr/local/bin/convert


# ============================================
# STORAGE PATHS (Optional - use defaults if not set)
# ============================================
VIDEO_OUTPUT_DIR=videos
IMAGE_CACHE_DIR=images
PDF_OUTPUT_DIR=generated_pdfs
CHROMA_DB_DIR=chroma_db
```

### Step 3: Create Required Directories

```bash
# From project root
mkdir -p videos
mkdir -p images
mkdir -p generated_pdfs
mkdir -p chroma_db
mkdir -p assets
```

---

## 6. External Services Setup

### 6.1 Google Gemini AI Setup

1. Go to https://ai.google.dev/
2. Sign in with Google account
3. Create new project or select existing
4. Navigate to "Get API Key"
5. Create and copy API key
6. Add to `.env` as `GOOGLE_API_KEY`

**Test:**
```bash
cd backend
python -c "import google.generativeai as genai; import os; from dotenv import load_dotenv; load_dotenv(); genai.configure(api_key=os.getenv('GOOGLE_API_KEY')); print('Gemini connected!')"
```

### 6.2 Unsplash API Setup

1. Go to https://unsplash.com/developers
2. Register as developer
3. Create new application
4. Copy Access Key
5. Add to `.env` as `UNSPLASH_ACCESS_KEY`

**Test:**
```bash
python -c "import requests; import os; from dotenv import load_dotenv; load_dotenv(); r = requests.get('https://api.unsplash.com/photos/random', headers={'Authorization': f'Client-ID {os.getenv(\"UNSPLASH_ACCESS_KEY\")}'}, timeout=5); print('Unsplash connected!' if r.status_code == 200 else f'Error: {r.status_code}')"
```

### 6.3 Azure Text-to-Speech Setup

1. Go to https://portal.azure.com
2. Create resource → Cognitive Services → Speech
3. Create new resource or use existing
4. Copy Key and Region from "Keys and Endpoint"
5. Add to `.env`:
   - `AZURE_TTS_KEY=your_key`
   - `AZURE_TTS_REGION=your_region`

**Test:**
```bash
python -c "import azure.cognitiveservices.speech as speechsdk; import os; from dotenv import load_dotenv; load_dotenv(); config = speechsdk.SpeechConfig(subscription=os.getenv('AZURE_TTS_KEY'), region=os.getenv('AZURE_TTS_REGION')); print('Azure TTS connected!')"
```

---

## 7. Running the Application

### Step 1: Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 54300 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:54300
INFO:     Application startup complete
```

**Verify backend:**
- Open http://localhost:54300
- Should see: `{"message": "Welcome to BSK Training Optimization API", ...}`
- API Docs: http://localhost:54300/docs

### Step 2: Start Frontend (New Terminal)

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Navigate to frontend
cd frontend

# Start Streamlit
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 3: Access Application

1. **Frontend Interface**: http://localhost:8501
2. **Backend API**: http://localhost:54300
3. **API Documentation**: http://localhost:54300/docs

---

## 8. Verification & Testing

### 8.1 Backend Health Check

```bash
# Test root endpoint
curl http://localhost:54300/

# Test BSK endpoint
curl http://localhost:54300/bsk/?limit=5

# Test services endpoint
curl http://localhost:54300/services/?limit=5
```

### 8.2 Frontend Navigation Test

1. Open http://localhost:8501
2. Check sidebar navigation
3. Visit each page (01-09)
4. Verify data loads without errors

### 8.3 Video Generation Test

1. Navigate to "Training Video Generator" (Page 08)
2. Select any service
3. Choose "Manual Form Entry"
4. Fill in sample data:
   ```
   Service Description: Test service for verification
   Application Process: Step 1: Visit BSK, Step 2: Submit form
   Eligibility: All citizens
   Required Documents: ID proof, Address proof
   ```
5. Click "Generate Training Video"
6. Verify video is created in `videos/{service_id}/` directory

### 8.4 Recommendation Test

1. Navigate to "Service Recommendation" (Page 05)
2. Enter test service:
   ```
   Name: Digital Certificate Service
   Type: Government Service
   Description: Online certificate issuance for citizens
   ```
3. Click "Get Recommendations"
4. Verify results appear with scores

### 8.5 Analytics Test

1. Navigate to "Underperforming BSKs" (Page 06)
2. Set parameters:
   - Number of BSKs: 10
   - Sort: Lowest Score
3. Click "Analyze Performance"
4. Verify BSKs are displayed with scores

---

## 9. Production Deployment

### 9.1 Security Hardening

1. **Change default passwords**
2. **Use environment-specific .env files**
3. **Enable HTTPS**
4. **Restrict CORS origins** in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specific domains
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### 9.2 Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX idx_bsk_district ON dbo.ml_bsk_master(district_name);
CREATE INDEX idx_service_type ON dbo.ml_service_master(service_type);
CREATE INDEX idx_provision_bsk ON dbo.ml_provision(bsk_id, service_id);
```

### 9.3 Backend Production Config

**Use Gunicorn (Linux) or Hypercorn:**

```bash
# Install
pip install gunicorn

# Run
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:54300
```

### 9.4 Frontend Production Deployment

**Option 1: Streamlit Cloud**
1. Push code to GitHub
2. Connect at share.streamlit.io
3. Deploy from repository

**Option 2: Docker**
```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 9.5 Monitoring & Logging

**Enable logging:**

```python
# In main.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 10. Troubleshooting

### Issue 1: Database Connection Failed

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (pyodbc.OperationalError)
```

**Solutions:**
1. Verify SQL Server is running
2. Check DATABASE_URL format
3. Test ODBC driver:
   ```bash
   # Windows
   odbcad32.exe
   
   # Linux
   odbcinst -j
   ```
4. Verify firewall allows port 1433
5. Enable TCP/IP in SQL Server Configuration Manager

### Issue 2: ImageMagick Not Found

**Symptoms:**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solutions:**
1. Verify installation:
   ```bash
   magick --version
   ```
2. Check `IMAGEMAGICK_BINARY` path in `.env`
3. Add ImageMagick to PATH
4. Reinstall with "legacy utilities" option

### Issue 3: API Keys Invalid

**Symptoms:**
```
Error 401: Unauthorized
```

**Solutions:**
1. Verify API keys in `.env`
2. Check key hasn't expired
3. Verify account has sufficient quota
4. Test each API individually (see Section 6)

### Issue 4: ChromaDB Permission Error

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'chroma_db'
```

**Solutions:**
```bash
# Fix permissions
chmod -R 755 chroma_db/

# Or recreate directory
rm -rf chroma_db/
mkdir chroma_db
```

### Issue 5: Video Generation Timeout

**Symptoms:**
```
TimeoutError: Video generation exceeded time limit
```

**Solutions:**
1. Reduce slide count (split long content)
2. Use shorter audio narration
3. Increase timeout in `video_utils.py`
4. Check internet connection (for image downloads)

### Issue 6: Port Already in Use

**Symptoms:**
```
ERROR: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find process using port
# Linux/Mac
lsof -i :54300
kill -9 <PID>

# Windows
netstat -ano | findstr :54300
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 54301
```

### Issue 7: Module Import Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Solutions:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Or install specific package
pip install <package-name>

# Verify Python path
python -c "import sys; print(sys.path)"
```

---

## 📝 Post-Setup Checklist

- [ ] Database connected and tables created
- [ ] All API keys configured and tested
- [ ] Backend server running on port 54300
- [ ] Frontend accessible on port 8501
- [ ] API documentation accessible
- [ ] Sample video generated successfully
- [ ] Recommendations working
- [ ] All Streamlit pages load without errors
- [ ] Directories created (videos, images, etc.)
- [ ] ImageMagick installed and configured
- [ ] Logs directory created (optional)
- [ ] Backup strategy in place (production)

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check logs**: Look in `app.log` or terminal output
2. **Review API docs**: http://localhost:54300/docs
3. **Test individual components**: Use Python REPL to test modules
4. **GitHub Issues**: Submit detailed bug reports
5. **Documentation**: Review README.md and code comments

---

## 🔄 Next Steps

After successful setup:

1. **Import real data** into database
2. **Initialize embeddings** (Page 05)
3. **Create training videos** for key services
4. **Set up monitoring** and alerts
5. **Train team** on platform usage
6. **Configure backups** (database + videos)
7. **Plan rollout** to BSK centers

---

**Setup Complete! 🎉**

Your BSK Training Optimization System is now ready to use. Visit the frontend at http://localhost:8501 to get started!