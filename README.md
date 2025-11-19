# Doctor-AI: Medical Diagnostic Support System

An AI-powered clinical decision support system that analyzes patient symptoms and suggests potential diagnoses using advanced vector similarity search and medical knowledge bases.

## Features

- Analyzes patient symptoms to identify potential medical conditions
- Provides differential diagnoses ranked by confidence
- Detects rare diseases through HPO (Human Phenotype Ontology)
- Flags life-threatening symptoms requiring immediate attention
- Uses BioBERT/PubMedBERT for semantic symptom matching
- Includes demo dashboard with analytics

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, Qdrant vector database
- **Frontend**: React 18, Vite
- **ML/NLP**: BioBERT, PubMedBERT
- **Deployment**: Docker

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- 8GB+ RAM

### Installation

```bash
# Clone repository
git clone https://github.com/Abrar5510/Doctor-Ai.git
cd Doctor-Ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Docker services
docker compose up -d

# Initialize database
python scripts/seed_data.py

# Start backend
python -m src.main
# API runs at http://localhost:8000

# In a new terminal, start frontend
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

### Access Points

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## Testing

```bash
# Test the API
python scripts/test_api.py
```

## Configuration

Create `.env` file (see `.env.example`):

```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
```

## Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for detailed deployment instructions including:
- Docker deployment
- Cloud deployment (Vercel, Railway, etc.)
- Environment configuration

Quick Docker deployment:
```bash
docker compose up -d
```

## Architecture

See **[ARCHITECTURE.md](./ARCHITECTURE.md)** for system architecture details.

## Important Disclaimer

⚠️ **This system is for research and educational purposes only**. It is designed to assist healthcare professionals, NOT to replace physician judgment or provide definitive diagnoses. All suggestions require human review and clinical validation.

## Additional Documentation

- **Setup Guide**: [SETUP.md](./SETUP.md) - Troubleshooting and common issues
- **Deployment Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment options
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

## License

MIT License - see [LICENSE](./LICENSE) file

---

**GitHub**: https://github.com/Abrar5510/Doctor-Ai
