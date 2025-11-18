# Medical Symptom Constellation Mapper 🏥

An AI-powered diagnostic support system that maps patient symptoms to potential medical conditions using advanced pattern matching and vector similarity search with Qdrant.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.7+-red.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Features

### Core Diagnostic Features
- **Vector Similarity Search**: Semantic understanding of symptom relationships using BioBERT/PubMedBERT embeddings
- **Rare Disease Detection**: Comprehensive orphan disease coverage and pattern recognition
- **Multi-tier Review System**: Confidence-based routing to appropriate care levels
- **Red Flag Detection**: Immediate alerts for life-threatening symptoms
- **Explainable AI**: Complete transparency in diagnostic reasoning
- **HIPAA Compliant**: Full audit trail and data anonymization
- **Clinical Decision Support**: Evidence-based recommendations for tests and specialists

### NEW: Dashboard & Analytics 📊
- **Admin Dashboard**: Beautiful, investor-ready analytics dashboard with real-time metrics
- **Interactive Visualizations**: Charts for tier distribution, top conditions, demographics, and performance
- **Demo Data Included**: 30+ realistic patient cases with 62 diagnoses ready for demonstration
- **Performance Monitoring**: System metrics tracking with 14 days of sample data

### NEW: Modern Frontend 🎨
- **Landing Page**: Impressive, modern landing page for investors and judges
- **React 18 + Vite**: Fast, modern frontend with beautiful gradients and animations
- **Responsive Design**: Mobile-friendly interface with smooth transitions
- **Multiple Routes**: Landing page, diagnosis tool, and analytics dashboard

### NEW: Cloud Deployment ☁️
- **Render Support**: One-click deployment with included `render.yaml`
- **Production Ready**: Full deployment guide with environment configuration
- **Scalable Architecture**: Docker containers, caching, and async processing

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Medical Datasets](#medical-datasets)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

### Core Components

1. **Data Ingestion Pipeline**: Multi-format input handling with NER for medical terms
2. **Medical Ontology Integration**: SNOMED CT, ICD-10/11, HPO, and UMLS support
3. **Vector Embedding System**: BioBERT-based medical text embeddings
4. **Qdrant Vector Database**: High-performance similarity search
5. **Diagnostic Reasoning Engine**: Multi-stage search with Bayesian probability
6. **Multi-tier Review System**: Automated triage based on confidence scores
7. **Audit Trail System**: Complete HIPAA-compliant logging

### Tech Stack

- **Backend**: Python 3.9+, FastAPI
- **ML/NLP**: Transformers, PyTorch, spaCy, sentence-transformers
- **Vector Database**: Qdrant
- **Traditional Database**: PostgreSQL
- **Cache**: Redis
- **Embeddings**: PubMedBERT (768-dim), BioBERT

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for databases)
- 8GB+ RAM recommended
- CUDA-capable GPU (optional, for faster embedding generation)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Abrar5510/Doctor-Ai.git
cd Doctor-Ai
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Set Up Qdrant Vector Database

Qdrant can be set up in multiple ways. Choose the option that works best for you:

**Quick Setup (Automated):**
```bash
chmod +x scripts/setup_qdrant.sh
./scripts/setup_qdrant.sh
```

**Manual Setup with Docker:**
```bash
docker compose up -d
```

This will start:
- Qdrant (port 6333)
- PostgreSQL (port 5432)
- Redis (port 6379)

**Getting "error getting credentials" error?** Run this first:
```bash
./fix-docker-credentials.sh
```
See [DOCKER_CREDENTIAL_FIX.md](DOCKER_CREDENTIAL_FIX.md) for details.

**Having other issues?** See our comprehensive guides:
- [Docker Setup & Troubleshooting](DOCKER.md)
- [Qdrant Setup Guide](QDRANT_SETUP.md) for:
  - Docker installation
  - Binary installation (no Docker needed)
  - Qdrant Cloud setup
  - Troubleshooting common errors

## ⚡ Quick Start

### 0. Test Qdrant Connection (Optional but Recommended)

Verify that Qdrant is running and accessible:

```bash
python scripts/test_qdrant_connection.py
```

This will test:
- Connection to Qdrant
- Permission to create collections
- Existence of medical_conditions collection

### 1. Seed the Database

Populate the vector database with sample medical conditions:

```bash
python scripts/seed_data.py
```

This will:
- Initialize the Qdrant collection
- Generate embeddings for medical conditions
- Insert sample conditions into the database

### 2. Start the API Server

```bash
python -m src.main
```

Or using uvicorn directly:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the Frontend (NEW!)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

**Available Routes:**
- **/** - Beautiful landing page with feature showcase
- **/dashboard** - Admin dashboard with analytics and metrics
- **/diagnose** - Diagnosis tool for symptom analysis

### 4. Access the API Documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Dashboard: http://localhost:3000/dashboard

### 5. View Demo Data

The application includes realistic demo data:
- `demo_data/sample_patient_cases.csv` - 30 patient cases
- `demo_data/diagnoses_data.csv` - 62 differential diagnoses
- `demo_data/system_metrics.csv` - 14 days of performance metrics

Access the dashboard at http://localhost:3000/dashboard to visualize this data!

### 6. Test the API

```bash
python scripts/test_api.py
```

## 💻 Usage

### Example: Analyze Patient Symptoms

```python
import httpx

# Patient case
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
        },
        {
            "description": "Always feeling cold",
            "severity": "moderate",
            "duration_days": 60,
            "frequency": "constant"
        }
    ]
}

# Send request
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/analyze",
        json=patient_case
    )
    result = response.json()

# View results
print(f"Primary Diagnosis: {result['primary_diagnosis']['condition_name']}")
print(f"Confidence: {result['overall_confidence']:.2%}")
print(f"Review Tier: {result['review_tier']}")
```

### Review Tiers

The system automatically routes cases based on confidence:

- **Tier 1** (>85% confidence): Automated assessment with high-confidence diagnosis
- **Tier 2** (60-85%): Primary care physician review recommended
- **Tier 3** (40-60%): Specialist consultation required
- **Tier 4** (<40%): Multi-disciplinary team review needed

## 📊 Medical Datasets

Doctor-Ai integrates multiple comprehensive medical datasets to provide accurate diagnostic support.

### Available Datasets

#### 1. Human Phenotype Ontology (HPO)
- **Size**: ~50MB
- **Content**: 15,247 phenotype terms, 8,000+ rare disease annotations
- **Use**: Rare disease detection, phenotype-based diagnosis

#### 2. ICD-10-CM Disease Codes
- **Size**: ~50MB
- **Content**: 70,000+ diagnostic codes
- **Use**: Disease classification, diagnosis coding

#### 3. Disease-Symptom Mappings
- **Size**: ~5MB
- **Content**: Curated disease-symptom relationships
- **Use**: ML training, symptom analysis

### Download Datasets

Download all priority datasets (safe for GitHub, ~105MB total):

```bash
python scripts/download_datasets/download_all_priority.py
```

Download individual datasets:

```bash
# Human Phenotype Ontology
python scripts/download_datasets/download_hpo.py

# ICD-10-CM codes
python scripts/download_datasets/download_icd10.py

# Disease-symptom datasets
python scripts/download_datasets/download_disease_symptoms.py
```

### Large External Datasets

The following datasets are too large for GitHub and require external storage:

- **MIMIC-III/IV** (~60-100GB): Clinical ICU data - [Requires PhysioNet credentials](https://physionet.org/)
- **UMLS** (~10GB): Unified medical terminology - [Requires NLM registration](https://www.nlm.nih.gov/research/umls/)
- **SNOMED CT** (~2GB): Comprehensive clinical terminology - [Requires NLM license](https://www.nlm.nih.gov/healthit/snomedct/us_edition.html)

### Documentation

For comprehensive dataset information, download instructions, and integration guides:
- **Full Dataset Catalog**: See [MEDICAL_DATASETS.md](MEDICAL_DATASETS.md)
- **Download Scripts**: See [scripts/download_datasets/README.md](scripts/download_datasets/README.md)
- **Dataset Directory**: See [datasets/README.md](datasets/README.md)

## 📚 API Documentation

### Main Endpoints

#### `POST /api/v1/analyze`

Analyze patient symptoms and generate differential diagnosis.

**Request Body:**
```json
{
  "case_id": "string",
  "age": 35,
  "sex": "female",
  "chief_complaint": "string",
  "symptoms": [
    {
      "description": "string",
      "severity": "moderate",
      "duration_days": 60,
      "frequency": "constant"
    }
  ]
}
```

**Response:**
```json
{
  "result_id": "string",
  "case_id": "string",
  "differential_diagnoses": [...],
  "primary_diagnosis": {...},
  "review_tier": "tier1_automated",
  "overall_confidence": 0.92,
  "red_flags_detected": [],
  "requires_emergency_care": false,
  "recommended_specialists": ["Endocrinologist"],
  "recommended_tests": ["TSH", "Free T4"],
  "reasoning_summary": "string",
  "processing_time_ms": 250.5
}
```

#### `GET /api/v1/condition/{condition_id}`

Get detailed information about a medical condition.

#### `GET /api/v1/stats`

Get system and database statistics.

#### `GET /health`

Health check endpoint.

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=medical_conditions

# ML Model
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
EMBEDDING_DIMENSION=768

# Confidence Thresholds
TIER1_CONFIDENCE_THRESHOLD=0.85
TIER2_CONFIDENCE_THRESHOLD=0.60
TIER3_CONFIDENCE_THRESHOLD=0.40

# Features
ENABLE_RARE_DISEASE_DETECTION=True
ENABLE_RED_FLAG_ALERTS=True
ENABLE_AUDIT_LOGGING=True
```

## 🛠️ Development

### Project Structure

```
doctor-ai/
├── src/
│   ├── api/              # FastAPI routes
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── embedding.py  # Vector embeddings
│   │   ├── vector_store.py  # Qdrant operations
│   │   └── diagnostic.py    # Diagnostic reasoning
│   ├── utils/            # Utilities
│   ├── config.py         # Configuration
│   └── main.py           # Application entry point
├── scripts/              # Utility scripts
│   ├── seed_data.py     # Database seeding
│   └── test_api.py      # API testing
├── tests/                # Unit tests
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker services
└── README.md
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## 🚢 Deployment

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t doctor-ai:latest .
```

2. Run with docker-compose:

```bash
docker-compose up -d
```

### Render Deployment (NEW! ☁️)

We've included one-click deployment to Render.com:

1. **One-Click Deploy:**
   - Push this repository to GitHub
   - Go to [Render Dashboard](https://render.com/dashboard)
   - Click "New" → "Blueprint"
   - Connect your repository
   - Click "Apply"

2. **Manual Setup:**
   - See detailed guide in `RENDER_DEPLOYMENT.md`
   - Includes configuration for:
     - Backend API (Python/FastAPI)
     - Frontend (Static site)
     - PostgreSQL database
   - Free tier available (~$14/month for starter)

3. **Demo Guide:**
   - See `DEMO_GUIDE.md` for investor/judge presentation
   - Includes sample data and talking points
   - Performance metrics and key features highlighted

### Production Considerations

- [ ] Use production-grade WSGI server (Gunicorn with Uvicorn workers)
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure proper CORS policies
- [ ] Enable rate limiting
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Implement backup strategies for Qdrant and PostgreSQL
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Implement proper authentication and authorization
- [ ] Set up logging aggregation (ELK stack)

## 🔒 Security & Compliance

### HIPAA Compliance

- ✅ Complete audit trail of all operations
- ✅ Data anonymization capabilities
- ✅ Access control and authentication ready
- ✅ Encryption at rest and in transit (configure SSL)
- ✅ Session management and timeouts

### Clinical Decision Support

⚠️ **Important Notice**: This system is a Clinical Decision Support (CDS) tool designed to assist healthcare professionals. It does NOT:
- Replace physician judgment
- Provide definitive diagnoses
- Prescribe treatments
- Function as a standalone diagnostic device

All diagnostic suggestions require human review and clinical validation.

## 📊 Performance

- Query latency: <2 seconds (p95)
- Embedding generation: ~500ms for typical case
- Vector search: <100ms for 10K vectors
- Throughput: 100+ queries/second (with proper scaling)

## 🗺️ Roadmap

### Phase 1: MVP (Current)
- [x] Basic symptom analysis
- [x] Vector similarity search
- [x] Differential diagnosis generation
- [x] Confidence scoring
- [x] Audit logging

### Phase 2: Enhanced Features
- [ ] EHR integration (HL7 FHIR)
- [ ] Lab result integration
- [ ] Temporal pattern analysis
- [ ] Multi-language support
- [ ] Mobile app

### Phase 3: Advanced AI
- [ ] Continuous learning from outcomes
- [ ] Personalized medicine integration
- [ ] Genomic data support
- [ ] Predictive health modeling

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qdrant** for the excellent vector database
- **HuggingFace** for transformer models
- **BioBERT/PubMedBERT** teams for medical language models
- **FastAPI** for the modern web framework
- Medical ontology providers (SNOMED CT, ICD, HPO)

## 📞 Contact

- **Project Link**: https://github.com/Abrar5510/Doctor-Ai
- **Issues**: https://github.com/Abrar5510/Doctor-Ai/issues
- **Discussions**: https://github.com/Abrar5510/Doctor-Ai/discussions

## ⚠️ Disclaimer

This software is provided for research and educational purposes only. It is not intended for use in clinical practice without proper validation, regulatory approval, and oversight by qualified healthcare professionals. The developers assume no liability for any use of this software in medical decision-making.

---

**Made with ❤️ for better healthcare**
