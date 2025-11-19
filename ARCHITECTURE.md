# System Architecture

## Overview

Doctor-AI uses vector similarity search to match patient symptoms to potential medical conditions.

## System Diagram

```
┌─────────────────────┐
│   React Frontend    │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  - Route handlers   │
│  - Validation       │
└──────────┬──────────┘
           │
           ├──────────┬──────────┬──────────┐
           ▼          ▼          ▼          ▼
      ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
      │Qdrant  │ │Embedding││Postgres││ Redis  │
      │Vector  │ │Service ││   DB   ││ Cache  │
      │  DB    │ │(BioBERT)│        │        │
      └────────┘ └────────┘ └────────┘ └────────┘
```

## Core Components

### 1. API Layer (`src/api/`)
- FastAPI application with route handlers
- Request validation with Pydantic
- Authentication and authorization

### 2. Services (`src/services/`)

**Diagnostic Service**
- Symptom analysis and pattern matching
- Differential diagnosis generation
- Confidence scoring (0-100%)
- Red flag detection for emergencies

**Embedding Service**
- Converts text to 768-dimensional vectors
- Uses BioBERT/PubMedBERT models
- GPU acceleration when available

**Vector Store Service**
- Manages Qdrant database operations
- Similarity search (cosine distance)

### 3. Data Layer

**Qdrant Vector Database**
- Stores medical condition embeddings
- Fast similarity search (<100ms)

**PostgreSQL Database**
- Patient case records
- Diagnosis history
- Audit logs

**Redis Cache**
- Embedding cache
- Query result cache

## Data Flow

### Symptom Analysis Pipeline

```
1. Client submits symptoms
   ↓
2. API validates request
   ↓
3. Embedding Service generates symptom vectors
   ↓
4. Vector Store searches for similar conditions
   ↓
5. Diagnostic Service ranks and scores results
   ↓
6. Results returned to client
   ↓
7. Case saved to PostgreSQL
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
    vector_similarity * 0.5 +    # Cosine similarity
    symptom_overlap * 0.3 +      # Matching symptoms
    temporal_match * 0.1 +       # Duration patterns
    demographic_fit * 0.1        # Age/sex match
)
```

### Triage Levels

- **Tier 1** (>85%): High-confidence automated assessment
- **Tier 2** (60-85%): Primary care physician review
- **Tier 3** (40-60%): Specialist consultation
- **Tier 4** (<40%): Multi-disciplinary team review

## Technology Stack

### Backend
- Python 3.9+ with FastAPI
- Transformers (HuggingFace)
- PyTorch
- Uvicorn ASGI server

### Databases
- Qdrant - Vector similarity search
- PostgreSQL - Structured data
- Redis - Caching layer

### ML Models
- PubMedBERT - 768-dim biomedical embeddings
- BioBERT - Alternative medical language model

### Medical Ontologies
- ICD-10 - Disease classification
- HPO - Human phenotype ontology
- SNOMED CT - Clinical terminology

## Project Structure

```
doctor-ai/
├── src/
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── main.py           # Application entry
├── frontend/             # React application
├── scripts/              # Utility scripts
├── datasets/             # Medical datasets
└── docker-compose.yml    # Service orchestration
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions.

---

For implementation details, see source code in `src/` directory.
