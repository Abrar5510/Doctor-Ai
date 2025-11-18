# System Architecture

High-level overview of Doctor-AI's architecture.

## Overview

Doctor-AI is a clinical decision support system that uses vector similarity search and AI reasoning to map patient symptoms to potential medical conditions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                           │
│              (React Frontend, API Clients)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                               │
│                    (FastAPI)                                 │
│  - Route handlers                                            │
│  - Request validation                                        │
│  - Authentication                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Diagnostic  │  │   Embedding  │  │AI Assistant  │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Vector Store │  │   Ontology   │                        │
│  │   Service    │  │   Service    │                        │
│  └──────────────┘  └──────────────┘                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Qdrant     │  │  PostgreSQL  │  │    Redis     │      │
│  │   Vector DB  │  │  Relational  │  │    Cache     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Gateway (`src/api/`)
- **FastAPI Application**: Handles HTTP requests and responses
- **Route Handlers**: Endpoint definitions for diagnosis, export, monitoring
- **Authentication**: JWT-based user authentication
- **Validation**: Pydantic models for request/response validation

### 2. Service Layer (`src/services/`)

#### Diagnostic Service
- Symptom analysis and pattern matching
- Differential diagnosis generation
- Confidence scoring (0-100%)
- Red flag detection for emergencies
- Review tier assignment (Tier 1-4)

#### Embedding Service
- Converts text to vector embeddings (768-dimensional)
- Uses BioBERT/PubMedBERT models
- GPU acceleration when available
- Caching for performance

#### AI Assistant Service
- Natural language explanations
- Follow-up question generation
- Medical report creation
- Supports OpenAI GPT-4 or local LLMs

#### Vector Store Service
- Manages Qdrant vector database operations
- Similarity search (cosine distance)
- Index management and optimization

### 3. Data Layer

#### Qdrant Vector Database
- Stores medical condition embeddings
- Fast similarity search (<100ms)
- Payload: condition name, ICD-10, symptoms, metadata

#### PostgreSQL Database
- Patient case records
- Diagnosis history
- Audit logs (HIPAA compliance)
- System metrics

#### Redis Cache
- Embedding cache (30-day TTL)
- Query result cache (1-hour TTL)
- Performance metrics

## Data Flow

### Symptom Analysis Pipeline

```
1. Client submits symptoms
   ↓
2. API validates and parses request
   ↓
3. Embedding Service generates symptom vectors
   ↓
4. Vector Store searches for similar conditions
   ↓
5. Diagnostic Service ranks and scores results
   ↓
6. AI Assistant enhances with explanations (optional)
   ↓
7. Results returned to client
   ↓
8. Case saved to PostgreSQL (audit trail)
```

## Diagnostic Algorithm

### Multi-Stage Search

1. **Broad Search**: All symptoms combined (top 50 candidates)
2. **Focused Search**: Chief complaint only (top 20 candidates)
3. **Rare Disease Search**: Filter for rare conditions (top 10)
4. **Fusion & Ranking**: Merge and rerank by confidence

### Confidence Scoring

```python
confidence = (
    vector_similarity * 0.5 +      # Cosine similarity
    symptom_overlap * 0.3 +        # Matching symptoms
    temporal_match * 0.1 +         # Duration patterns
    demographic_fit * 0.1          # Age/sex match
)
```

### Triage Logic

- **Tier 1** (>85%): High-confidence automated assessment
- **Tier 2** (60-85%): Primary care physician review
- **Tier 3** (40-60%): Specialist consultation
- **Tier 4** (<40%): Multi-disciplinary team review

## Technology Stack

### Backend
- **Python 3.9+** with FastAPI
- **Transformers** (HuggingFace) for ML models
- **PyTorch** for deep learning
- **Uvicorn** ASGI server

### Databases
- **Qdrant 1.7+** - Vector similarity search
- **PostgreSQL 14+** - Structured data
- **Redis 7+** - Caching layer

### ML Models
- **PubMedBERT** - 768-dim biomedical embeddings
- **BioBERT** - Alternative medical language model
- **GPT-4/Llama2** - AI explanations (optional)

### Medical Ontologies
- **SNOMED CT** - Clinical terminology
- **ICD-10/11** - Disease classification
- **HPO** - Human phenotype ontology (15K+ terms)
- **UMLS** - Unified medical language system

## Performance

- **Query Latency**: <2 seconds (p95)
- **Embedding Generation**: ~500ms per case
- **Vector Search**: <100ms for 10K vectors
- **Throughput**: 100+ queries/second
- **Cache Hit Rate**: 90%+ for repeat queries

## Scalability

### Horizontal Scaling
- Stateless FastAPI instances behind load balancer
- Qdrant cluster with sharding
- PostgreSQL read replicas
- Redis cluster

### Caching Strategy
- **L1**: In-memory application cache
- **L2**: Redis distributed cache
- **L3**: Database query cache

## Security & Compliance

### HIPAA Compliance
- Complete audit trail of all operations
- Data anonymization capabilities
- Encryption at rest and in transit (TLS 1.3)
- Role-based access control
- Session management with JWT

### Security Features
- API key authentication
- Rate limiting (Redis-based)
- Input validation and sanitization
- SQL injection protection (ORM)
- XSS protection

## Deployment

### Docker Deployment
```bash
docker build -t doctor-ai:latest .
docker compose up -d
```

### Cloud Deployment
- **Render.com**: One-click deploy with `render.yaml`
- **AWS/GCP/Azure**: Container-based deployment
- **Kubernetes**: Helm charts (future)

## Project Structure

```
doctor-ai/
├── src/
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   ├── utils/            # Utilities
│   └── main.py           # Application entry
├── scripts/              # Setup and utility scripts
├── tests/                # Test suite
├── frontend/             # React application
├── datasets/             # Medical datasets
├── demo_data/            # Demo cases
└── docker-compose.yml    # Service orchestration
```

## Future Enhancements

- **Microservices**: Split into independent services
- **Real-time**: WebSocket support for streaming
- **ML Optimization**: Fine-tuning on hospital data
- **FHIR Integration**: HL7 FHIR import/export
- **Mobile App**: React Native application
- **Advanced Analytics**: Grafana dashboards

---

For implementation details, see source code in `src/` directory.
