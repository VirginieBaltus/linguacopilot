<div align="center">

# LinguaCopilot

AI-Powered German Language Learning from YouTube

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture)

</div>

---

## Features

- YouTube Integration: Fetch educational videos from German channels
- Subtitle Processing: Download and clean subtitles using yt-dlp
- NLP Extraction: Extract vocabulary with spaCy and classify by CEFR levels
- AI Flashcard Generation: Create contextual examples using Ollama (local LLM)
- Dual-Mode Learning: Practice German→French and French→German
- Progress Tracking: Persistent statistics stored in SQLite

---

## Architecture
```
YouTube API → Videos → Subtitles → Cleaning → Vocabulary Extraction
                                                      ↓
                                              CEFR Classification
                                                      ↓
                                            Ollama (Local LLM)
                                                      ↓
                                              Flashcard Generation
                                                      ↓
                                            SQLite Database
                                                      ↓
                                         Streamlit Dashboard
```

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Data Collection | YouTube Data API v3, yt-dlp |
| NLP | spaCy, wordfreq |
| AI | Ollama (llama3.2:3b) |
| Database | SQLite |
| Frontend | Streamlit |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Deployment | Docker |

---

## Installation

### Prerequisites

- Python 3.11+
- Ollama (https://ollama.com/)
- YouTube Data API key (https://console.cloud.google.com/)

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/linguacopilot.git
cd linguacopilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download de_core_news_sm

# Setup Ollama
ollama pull llama3.2:3b

# Configure environment
cp .env.example .env
# Edit .env with your YouTube API key

# Initialize database
python src/database/schema.py
```

---

## Usage

### Run Pipeline
```bash
# Fetch videos
python src/youtube/channel_videos.py

# Download subtitles
python src/youtube/subtitles.py

# Clean text
python src/processing/cleaner.py

# Extract vocabulary
python src/processing/extractor.py

# Generate flashcards
python src/llm/flashcards.py

# Launch dashboard
streamlit run src/dashboard/app.py
```

### View Database
```bash
python view_db.py
```

---

## Dashboard Features

- Level Selection: Choose CEFR level (A1-C2)
- Dual Modes: German→French and French→German
- Progress Tracking: Persistent learning statistics
- Real-time Stats: Accuracy and word count
- Clean Interface: Responsive design

---

## Project Structure
```
linguacopilot/
├── .github/workflows/  # CI/CD pipelines
├── src/
│   ├── youtube/        # Video & subtitle fetching
│   ├── processing/     # NLP & extraction
│   ├── llm/            # Flashcard generation
│   ├── dashboard/      # Streamlit app
│   └── database/       # SQLite schema
├── tests/              # Unit tests
├── Dockerfile
└── README.md
```

---

## Testing
```bash
pytest tests/ -v
```

---

## Docker
```bash
docker build -t linguacopilot .
docker run -p 8501:8501 linguacopilot
```

---

## Future Improvements

- English translation support
- PostgreSQL migration for multi-user
- Spaced repetition algorithm
- Cloud deployment
- Anki export

---

## License

MIT License

---

## Contact

GitHub: @virginiebaltus

Project: https://github.com/VirginieBaltus/linguacopilot
