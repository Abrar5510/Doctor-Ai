# Doctor-AI: Medical Diagnostic Support System

An AI-powered clinical decision support system that analyzes patient symptoms and suggests potential diagnoses using advanced vector similarity search and medical knowledge bases.

## What It Does

Doctor-AI helps healthcare professionals by:
- Analyzing patient symptoms to identify potential medical conditions
- Providing differential diagnoses ranked by confidence
- Detecting rare diseases through comprehensive medical ontology integration
- Flagging life-threatening symptoms requiring immediate attention
- Recommending appropriate specialists and diagnostic tests
- Offering explainable AI reasoning for all suggestions

## Key Features

### Diagnostic Engine
- **Vector Similarity Search**: Uses BioBERT/PubMedBERT embeddings (768-dim) for semantic symptom matching
- **Rare Disease Detection**: Integration with HPO (Human Phenotype Ontology) for orphan disease coverage
- **Confidence-Based Triage**: Automatic routing to appropriate care levels (Tier 1-4)
- **Red Flag Alerts**: Immediate detection of emergency symptoms
- **Explainable AI**: Transparent reasoning for all diagnostic suggestions

### Dashboard & Analytics
- Real-time performance metrics and system monitoring
- Interactive visualizations for case distribution and demographics
- Demo data with 30+ realistic patient cases included

### Modern Tech Stack
- **Backend**: Python 3.9+, FastAPI, Qdrant vector database
- **ML/NLP**: BioBERT, PubMedBERT, Transformers
- **Frontend**: React 18, Vite, responsive design
- **Data**: PostgreSQL, Redis caching
- **Deployment**: Docker, containerized deployment

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- 8GB+ RAM recommended

### 1. Clone and Install

```bash
git clone https://github.com/Abrar5510/Doctor-Ai.git
cd Doctor-Ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Services

```bash
# Start Docker services (Qdrant, PostgreSQL, Redis)
docker compose up -d

# If you get Docker credential errors, run:
./fix-docker-credentials.sh
```

### 3. Initialize Database

```bash
# Seed with medical conditions
python scripts/seed_data.py
```

### 4. Start the Application

```bash
# Start backend API
python -m src.main
# API available at http://localhost:8000

# In a new terminal, start frontend
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:3000
```

### 5. Access the Application

- **Landing Page**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard
- **Diagnosis Tool**: http://localhost:3000/diagnose
- **API Docs**: http://localhost:8000/docs

## Demo & Testing

The system includes demo data for presentation:

```bash
# Test the API
python scripts/test_api.py

# View demo data
# - demo_data/sample_patient_cases.csv (30 cases)
# - demo_data/diagnoses_data.csv (62 diagnoses)
# - demo_data/system_metrics.csv (performance data)
```

## Example Usage

### Analyze Symptoms via API

```python
import httpx

patient_case = {
    "case_id": "case_001",
    "age": 35,
    "sex": "female",
    "chief_complaint": "Persistent fatigue and weight gain",
    "symptoms": [
        {
            "description": "Extreme fatigue for 2 months",
            "severity": "moderate",
            "duration_days": 60,
            "frequency": "constant"
        },
        {
            "description": "Unexplained weight gain of 15 pounds",
            "severity": "moderate",
            "duration_days": 90,
            "frequency": "progressive"
        }
    ]
}

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/analyze",
        json=patient_case
    )
    result = response.json()
    print(f"Primary Diagnosis: {result['primary_diagnosis']['condition_name']}")
    print(f"Confidence: {result['overall_confidence']:.2%}")
```

## Medical Datasets

Integrated medical knowledge bases:
- **HPO** (Human Phenotype Ontology): 15,247 phenotype terms, 8,000+ rare diseases
- **ICD-10-CM**: 70,000+ diagnostic codes
- **Disease-Symptom Mappings**: Curated relationships for ML training

Download datasets:
```bash
python scripts/download_datasets/download_all_priority.py
```

## Configuration

Key settings in `.env`:

```bash
# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ML Model
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
EMBEDDING_DIMENSION=768

# Confidence Thresholds
TIER1_CONFIDENCE_THRESHOLD=0.85  # Automated high-confidence
TIER2_CONFIDENCE_THRESHOLD=0.60  # Primary care review
TIER3_CONFIDENCE_THRESHOLD=0.40  # Specialist consultation

# Features
ENABLE_RARE_DISEASE_DETECTION=True
ENABLE_RED_FLAG_ALERTS=True
```

## Performance

- Query latency: <2 seconds (p95)
- Embedding generation: ~500ms per case
- Vector search: <100ms
- Throughput: 100+ queries/second (with scaling)

## Deployment

### Docker (Recommended)

The application is fully containerized and can run anywhere:

```bash
# Build and run all services
docker compose up -d

# Or build the backend image separately
docker build -t doctor-ai:latest .
docker run -p 8000:8000 doctor-ai:latest
```

### Vercel Deployment (Frontend + Backend)

Deploy both frontend and backend to Vercel as separate projects:

**Quick Start**:
```bash
# Deploy backend
vercel --prod --name doctor-ai-backend

# Deploy frontend
vercel --prod --name doctor-ai-frontend
```

See **[DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)** for step-by-step guide.

### Frontend Only Deployment

Deploy the frontend to any static hosting service:

**Vercel**:
```bash
vercel --prod
```

**Netlify**:
```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

**Or serve from the same container** - See `docker-compose.yml` for configuration

### Environment Variables

For production deployment, configure:
```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_HOST=your-redis-host
QDRANT_HOST=your-qdrant-host
SECRET_KEY=your-secret-key

# Frontend (optional - defaults to http://localhost:8000)
VITE_API_URL=https://your-backend-url.com
```

## Architecture

```
Client → FastAPI → Diagnostic Engine → Qdrant Vector DB
                 → Embedding Service → BioBERT/PubMedBERT
                 → AI Assistant → LLM (GPT-4/Llama2)
                 → PostgreSQL (cases, audit logs)
                 → Redis (caching)
```

**For detailed architecture**: See `ARCHITECTURE.md`

## Clinical Decision Support Notice

⚠️ **Important**: This system is a Clinical Decision Support (CDS) tool designed to **assist** healthcare professionals. It does NOT:
- Replace physician judgment
- Provide definitive diagnoses
- Prescribe treatments
- Function as a standalone diagnostic device

All diagnostic suggestions require human review and clinical validation.

## Security & Compliance

- ✅ HIPAA-compliant audit logging
- ✅ Data anonymization capabilities
- ✅ Encryption at rest and in transit
- ✅ Role-based access control ready
- ✅ Complete audit trail

## Additional Documentation

### Deployment Guides
- **Quick Start**: `DEPLOYMENT_QUICK_START.md` - Fast Vercel deployment
- **Separate Vercel Projects**: `VERCEL_SEPARATE_DEPLOYMENTS.md` - Frontend + Backend on Vercel
- **Hybrid Deployment**: `VERCEL_DEPLOYMENT.md` - Frontend on Vercel, Backend elsewhere
- **General Deployment**: `DEPLOYMENT.md` - All deployment options

### Other Documentation
- **Testing Guide**: `TESTING.md`
- **Security Policy**: `SECURITY.md`
- **Demo Guide**: `DEMO_GUIDE.md`
- **Architecture Details**: `ARCHITECTURE.md`
- **Contributing**: `CONTRIBUTING.md`

## License

MIT License - see `LICENSE` file

## Disclaimer

This software is provided for research and educational purposes. Not intended for clinical practice without proper validation, regulatory approval, and oversight by qualified healthcare professionals.

---

**GitHub**: https://github.com/Abrar5510/Doctor-Ai
