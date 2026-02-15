\# 🇩🇪 LinguaCopilot



A personal language learning tool that extracts vocabulary from YouTube subtitles and creates AI-powered flashcards using local LLM.



!\[Python](https://img.shields.io/badge/Python-3.11-blue)

!\[SQLite](https://img.shields.io/badge/Database-SQLite-green)

!\[Streamlit](https://img.shields.io/badge/UI-Streamlit-red)



\## Features



\- YouTube Integration: Automatically fetch videos from educational German channels (DW Deutsch)

\- Subtitle Processing: Download and clean German subtitles using yt-dlp

\- NLP-Powered Extraction: Extract vocabulary with spaCy and classify by CEFR levels (A1-C2)

\- AI Flashcard Generation: Create contextual example sentences using Ollama (llama3.2:3b)

\- Interactive Dashboard: Learn with dual-mode flashcards (DE→FR and FR→DE) using Streamlit

\- Progress Tracking: Persistent learning statistics stored in SQLite

\- SQLite Database: All data stored locally for privacy and offline use



\## Architecture

```

YouTube API → Videos → Subtitles → Cleaning → Vocabulary Extraction

&nbsp;                                                     ↓

&nbsp;                                             CEFR Classification

&nbsp;                                                     ↓

&nbsp;                                           Ollama (Local LLM)

&nbsp;                                                     ↓

&nbsp;                                             Flashcard Generation

&nbsp;                                                     ↓

&nbsp;                                           SQLite Database

&nbsp;                                                     ↓

&nbsp;                                        Streamlit Dashboard

```



\## Tech Stack



\- Data Collection: YouTube Data API v3, yt-dlp

\- NLP: spaCy (de\_core\_news\_sm), wordfreq

\- AI: Ollama (llama3.2:3b) for local LLM inference

\- Database: SQLite

\- Frontend: Streamlit

\- Testing: pytest

\- CI/CD: GitHub Actions

\- Containerization: Docker



\## Installation



\### Prerequisites



\- Python 3.11+

\- Ollama (https://ollama.com/)

\- YouTube Data API key (https://console.cloud.google.com/)



\### Setup



1\. Clone the repository

```bash

git clone https://github.com/yourusername/linguacopilot.git

cd linguacopilot

```



2\. Create virtual environment

```bash

python -m venv venv

source venv/bin/activate  # On Windows: venv\\Scripts\\activate

```



3\. Install dependencies

```bash

pip install -r requirements.txt

python -m spacy download de\_core\_news\_sm

```



4\. Install and setup Ollama

```bash

ollama pull llama3.2:3b

```



5\. Configure environment variables

```bash

cp .env.example .env

\# Edit .env and add your YouTube API key

```



Required .env variables:

```

YOUTUBE\_API\_KEY=your\_api\_key\_here

CHANNEL\_ID=UCxUWIEL-USsiPak0Qy6\_vVg

```



6\. Initialize database

```bash

python src/database/schema.py

```



\## Usage



\### Run the complete pipeline

```bash

\# 1. Fetch videos from YouTube

python src/youtube/channel\_videos.py



\# 2. Download subtitles

python src/youtube/subtitles.py



\# 3. Clean subtitles

python src/processing/cleaner.py



\# 4. Extract vocabulary with CEFR levels

python src/processing/extractor.py



\# 5. Generate flashcards (requires Ollama running)

python src/llm/flashcards.py



\# 6. Launch dashboard

streamlit run src/dashboard/app.py

```



\### View database contents

```bash

python view\_db.py

```



\## Dashboard Features



\- Level Selection: Choose your CEFR level (A1, A2, B1, B2, C1, C2)

\- Dual Learning Modes: German to French and French to German

\- Persistent Progress: All learning stats saved to database

\- Real-time Statistics: Track words practiced, accuracy, and improvement

\- Responsive Design: Clean, user-friendly interface



\## Screenshots



!\[Dashboard](docs/images/dashboard.png)



!\[Statistics](docs/images/stats.png)



\## Database Schema

```sql

videos (id, title, description, published\_at, created\_at)

vocabulary (id, word, level, count, created\_at)

flashcards (id, word, level, sentence\_de, sentence\_fr, created\_at)

user\_progress (id, word, correct\_count, incorrect\_count, last\_seen)

```



\## Testing

```bash

pytest tests/ -v

```



\## Docker

```bash

\# Build image

docker build -t linguacopilot .



\# Run container

docker run -p 8501:8501 linguacopilot

```



\## Project Structure

```

linguacopilot/

├── .github/workflows/     # CI/CD pipelines

├── src/

│   ├── youtube/          # Video \& subtitle fetching

│   ├── processing/       # Cleaning \& extraction

│   ├── llm/              # Flashcard generation

│   ├── dashboard/        # Streamlit app

│   └── database/         # Schema \& utilities

├── tests/                # Unit tests

├── data/                 # Database \& raw files (gitignored)

├── Dockerfile

├── requirements.txt

└── README.md

```



\## Future Improvements



\- Support for English translations

\- Migrate to PostgreSQL for multi-user support

\- Add spaced repetition algorithm (SM-2)

\- Support multiple languages

\- Deploy to cloud (AWS Lambda + RDS)

\- User authentication

\- Export flashcards to Anki



\## License



MIT License



\## Contact



GitHub: \[@VirginieBaltus](https://github.com/VirginieBaltus)



Project Link: https://github.com/VirgnieBaltus/linguacopilot

