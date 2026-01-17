# BSK Training Video Generator - Setup Guide

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Tesseract OCR** - [Installation Guide](https://github.com/tesseract-ocr/tesseract)
   - Windows: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
3. **ImageMagick** - [Download](https://imagemagick.org/script/download.php)
   - Windows: Download and run installer
   - Mac: `brew install imagemagick`
   - Linux: `sudo apt-get install imagemagick`

### Required API Keys
You'll need accounts and API keys for:
- **Google Gemini** - [Get API Key](https://makersuite.google.com/app/apikey)
- **Unsplash** - [Get Access Key](https://unsplash.com/oauth/applications)

---

## 🚀 Installation Steps

### 1. Clone or Download the Project
```bash
cd training-video-generation
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**Copy the template:**
```bash
# Windows
copy .env.template .env

# Mac/Linux
cp .env.template .env
```

**Edit `.env` file and add your API keys:**
```bash
GOOGLE_API_KEY=your_actual_google_api_key_here
UNSPLASH_ACCESS_KEY=your_actual_unsplash_key_here
```

### 5. Verify Configuration
```bash
python config.py
```

This will check:
- ✅ All API keys are set
- ✅ Tesseract OCR is installed
- ✅ ImageMagick is installed
- ✅ Required directories exist
- ✅ Asset files are present

---

## 📁 Project Structure

```
training-video-generation/
├── assets/                    # Static assets
│   ├── avatar/
│   │   └── avatar.png        # Avatar image
│   ├── default_background.jpg # Fallback image
│   └── style.css             # Streamlit styling
│
├── services/                  # External API integrations
│   ├── gemini_service.py     # Gemini AI for slide generation
│   ├── openai_service.py     # Alternative: OpenAI GPT
│   └── unsplash_service.py   # Image fetching
│
├── utils/                     # Core utilities
│   ├── audio_utils.py        # Text-to-speech generation
│   ├── avatar_utils.py       # Avatar animation
│   ├── image_utils.py        # Image processing
│   ├── pdf_extractor.py      # PDF text extraction
│   ├── pdf_utils.py          # PDF generation
│   ├── service_utils.py      # Service content utilities
│   └── video_utils.py        # Video composition
│
├── generated_pdfs/            # Output: Generated PDFs
├── images/                    # Output: Downloaded images cache
├── output_videos/             # Output: Final training videos
│
├── app.py                     # Main Streamlit application
├── config.py                  # Configuration management
├── .env                       # Your API keys (DO NOT COMMIT!)
├── .env.template              # Template for .env
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## ▶️ Running the Application

### Start the Web Interface
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 🧪 Testing Individual Components

### Test PDF Extraction
```bash
python utils/pdf_extractor.py path/to/your/document.pdf
```

### Test Slide Generation
```bash
python services/gemini_service.py
# You'll be prompted to enter a PDF path
```

### Test Configuration
```bash
python config.py
```

---

## ⚠️ Common Issues & Solutions

### Issue: "GOOGLE_API_KEY not found"
**Solution:** Make sure you've created `.env` file and added your API key:
```bash
GOOGLE_API_KEY=your_key_here
```

### Issue: "Tesseract OCR not found"
**Solution:** 
- Install Tesseract OCR
- Restart your terminal/command prompt
- Run `python config.py` to verify detection

### Issue: "ImageMagick not found"
**Solution:**
- Install ImageMagick
- Make sure to check "Install legacy utilities" during Windows installation
- Restart your terminal/command prompt

### Issue: Video generation fails with codec error
**Solution:**
- Make sure ImageMagick is properly installed
- On Windows, verify the installation path in `config.py`

### Issue: No images loading from Unsplash
**Solution:**
- Check your `UNSPLASH_ACCESS_KEY` in `.env`
- Verify you're within Unsplash's rate limits (50 requests/hour for free tier)

---

## 🔒 Security Best Practices

### Never commit sensitive data:
- ✅ `.env` is in `.gitignore`
- ✅ API keys are loaded from environment
- ❌ Never hardcode API keys in source files
- ❌ Never commit `.env` to version control

### Before sharing code:
1. Remove all API keys from code files
2. Check `.env` is not included
3. Verify `.gitignore` is working: `git status`

---

## 📦 Dependencies

Key Python packages used:
- `streamlit` - Web interface
- `moviepy` - Video composition
- `edge-tts` - Text-to-speech
- `google-generativeai` - Gemini AI
- `pymupdf` (fitz) - PDF processing
- `pytesseract` - OCR
- `Pillow` - Image processing
- `python-dotenv` - Environment variables

---

## 🤝 Contributing

1. Always use environment variables for secrets
2. Test configuration with `python config.py` before committing
3. Follow the existing project structure
4. Update this guide if you add new dependencies

---

## 📞 Support

If you encounter issues:
1. Run `python config.py` to check configuration
2. Check the common issues section above
3. Verify all prerequisites are installed
4. Check API key validity and rate limits

---

## 📄 License

[Your License Here]