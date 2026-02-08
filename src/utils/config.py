# 🧠 LinguaCopilot

Personal AI language learning assistant with Retrieval-Augmented Generation (RAG) system.

## 🚀 Quick Start

`ash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your settings

# 3. Run the application
python -m src.api.main
linguacopilot/
├── data/               # Data storage
│   ├── raw/           # Raw data from APIs
│   ├── processed/     # Cleaned data
│   └── embeddings/    # Vector embeddings
├── src/               # Source code
│   ├── api/          # FastAPI application
│   ├── embedding/    # Embedding utilities
│   ├── models/       # Data models
│   └── utils/        # Helper functions
├── tests/            # Test suite
├── docker/           # Docker configurations
├── scripts/          # Utility scripts
└── docs/             # Documentation

---

## **🐍 ÉTAPE 6 : CRÉE TON PREMIER FICHIER PYTHON**

### **6.1 Crée src/utils/config.py :**
`powershell
New-Item -Path src\utils\config.py -ItemType File -Force
@"
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration manager for the application."""
    
    # API Keys
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    # App
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Databases
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
