# System Architecture

This document provides a comprehensive overview of the Doctor-AI Medical Symptom Constellation Mapper architecture.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [API Design](#api-design)
- [Scalability](#scalability)
- [Security Architecture](#security-architecture)

## System Overview

Doctor-AI is a clinical decision support system that uses vector similarity search and AI reasoning to map patient symptoms to potential medical conditions.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                           │
│  (Web UI, Mobile App, CLI, Third-party Integrations)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Application (src/api/)                      │   │
│  │  - Route handlers                                    │   │
│  │  - Request validation                                │   │
│  │  - Response formatting                               │   │
│  │  - Authentication/Authorization                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Internal API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Diagnostic  │  │   Embedding  │  │AI Assistant  │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Vector Store │  │     NER      │  │  Ontology    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Data Access
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Qdrant     │  │  PostgreSQL  │  │    Redis     │      │
│  │   Vector DB  │  │  Relational  │  │    Cache     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Medical     │  │   Audit      │                        │
│  │  Ontologies  │  │   Logs       │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Client Layer

**Responsibilities:**
- User interaction
- Data input/display
- Client-side validation

**Interfaces:**
- Web applications (Swagger UI, ReDoc)
- Mobile applications (future)
- CLI tools
- Third-party integrations via REST API

### 2. API Gateway Layer

**Location:** `src/api/`

**Components:**
- **FastAPI Application** (`src/main.py`)
  - ASGI application server
  - Middleware configuration
  - CORS handling
  - Request/response lifecycle

- **Route Handlers** (`src/api/routes.py`)
  - Endpoint definitions
  - Request validation (Pydantic)
  - Response serialization
  - Error handling

**Key Features:**
- Auto-generated OpenAPI documentation
- Request/response validation
- Type safety with Pydantic models
- Async request handling

### 3. Service Layer

**Location:** `src/services/`

**Components:**

#### Diagnostic Service (`diagnostic.py`)

**Responsibilities:**
- Symptom analysis
- Differential diagnosis generation
- Confidence scoring
- Red flag detection
- Review tier assignment

**Key Methods:**
```python
class DiagnosticService:
    async def analyze_symptoms(
        symptoms: List[Symptom],
        patient_context: PatientContext
    ) -> DiagnosisResult

    async def generate_differential(
        primary_matches: List[Match]
    ) -> List[Diagnosis]

    async def calculate_confidence(
        symptoms: List[Symptom],
        condition: Condition
    ) -> float
```

**Algorithms:**
- Vector similarity search (cosine similarity)
- Bayesian probability estimation
- Pattern matching
- Confidence aggregation

#### Embedding Service (`embedding.py`)

**Responsibilities:**
- Text to vector conversion
- Model management
- Batch processing
- Caching embeddings

**Key Features:**
- BioBERT/PubMedBERT embeddings (768-dim)
- GPU acceleration (when available)
- Batch processing for efficiency
- Embedding cache

**Model Pipeline:**
```
Text Input → Tokenization → BERT Encoding → Pooling → Normalization → Vector (768-dim)
```

#### AI Assistant Service (`ai_assistant.py`)

**Responsibilities:**
- Natural language generation
- Follow-up question generation
- Medical report creation
- Explanation simplification

**Key Features:**
- OpenAI GPT-4 integration
- Local LLM support (Ollama)
- Template-based fallbacks
- Prompt engineering for medical accuracy

#### Vector Store Service (`vector_store.py`)

**Responsibilities:**
- Vector database operations
- Similarity search
- Index management
- Collection operations

**Key Operations:**
```python
class VectorStoreService:
    async def search(
        query_vector: List[float],
        top_k: int,
        filters: Optional[Dict]
    ) -> List[ScoredPoint]

    async def upsert(
        points: List[Point]
    ) -> bool

    async def create_collection(
        collection_name: str,
        vector_size: int
    ) -> bool
```

### 4. Data Layer

**Components:**

#### Qdrant Vector Database

**Purpose:** Semantic similarity search for medical conditions

**Schema:**
```json
{
  "collection": "medical_conditions",
  "vector_size": 768,
  "distance": "Cosine",
  "payload": {
    "condition_id": "string",
    "condition_name": "string",
    "icd10_code": "string",
    "category": "string",
    "common_symptoms": ["array"],
    "rare_disease": "boolean",
    "severity": "string"
  }
}
```

**Indexes:**
- HNSW (Hierarchical Navigable Small World) for fast ANN search
- Payload indexes for filtering

#### PostgreSQL Database

**Purpose:** Structured data, audit logs, user data

**Tables:**
- `cases`: Patient case records
- `diagnoses`: Diagnosis results
- `audit_logs`: HIPAA-compliant audit trail
- `users`: User accounts (future)
- `sessions`: Session management

#### Redis Cache

**Purpose:** Performance optimization

**Cached Data:**
- Embedding vectors (temporary)
- API responses
- Session data
- Rate limiting counters

**TTL Strategy:**
- Embeddings: 1 hour
- API responses: 5 minutes
- Session data: 30 minutes

## Core Components

### 1. Data Ingestion Pipeline

```
Raw Input → Validation → NER → Normalization → Embedding → Vector Storage
```

**Steps:**

1. **Validation**: Pydantic schema validation
2. **NER**: Named Entity Recognition for medical terms
3. **Normalization**: SNOMED CT/ICD-10 code mapping
4. **Embedding**: Vector generation via BioBERT
5. **Storage**: Upsert to Qdrant

### 2. Query Processing Pipeline

```
Symptom Query → Embedding → Vector Search → Scoring → Ranking → AI Enhancement → Response
```

**Steps:**

1. **Query Embedding**: Convert symptoms to vector
2. **Vector Search**: Find similar conditions in Qdrant (top-K=50)
3. **Scoring**: Calculate confidence scores
4. **Ranking**: Sort by confidence + clinical relevance
5. **AI Enhancement**: Generate explanations, questions, reports
6. **Response**: Format and return results

### 3. Diagnostic Reasoning Engine

**Multi-Stage Search:**

1. **Stage 1: Broad Search**
   - Query: All symptoms combined
   - Candidates: Top 50 matches
   - Strategy: High recall

2. **Stage 2: Focused Search**
   - Query: Chief complaint only
   - Candidates: Top 20 matches
   - Strategy: High precision

3. **Stage 3: Rare Disease Search**
   - Query: All symptoms + rare disease filter
   - Candidates: Top 10 rare conditions
   - Strategy: Sensitivity for rare presentations

4. **Stage 4: Fusion & Ranking**
   - Merge results from all stages
   - Deduplicate
   - Rerank by combined score
   - Apply clinical rules

**Confidence Scoring:**

```python
confidence = (
    vector_similarity * 0.5 +
    symptom_overlap * 0.3 +
    temporal_match * 0.1 +
    demographic_fit * 0.1
)
```

**Triage Logic:**

- **Tier 1** (>85%): Automated high-confidence
- **Tier 2** (60-85%): Primary care review
- **Tier 3** (40-60%): Specialist consultation
- **Tier 4** (<40%): Multi-disciplinary review

### 4. Medical Ontology Integration

**Supported Ontologies:**

1. **SNOMED CT**
   - Concept mapping
   - Relationship traversal
   - Terminology normalization

2. **ICD-10/11**
   - Disease classification
   - Billing codes
   - Epidemiological coding

3. **HPO (Human Phenotype Ontology)**
   - Rare disease phenotypes
   - Gene-phenotype associations
   - Inheritance patterns

4. **UMLS**
   - Cross-terminology mapping
   - Unified concept IDs
   - Multi-language support

## Data Flow

### Symptom Analysis Flow

```
1. Client Request
   POST /api/v1/analyze
   {
     "case_id": "...",
     "symptoms": [...],
     "age": 35,
     "sex": "female"
   }

2. API Layer
   - Validate request (Pydantic)
   - Extract symptoms
   - Create patient context

3. Service Layer
   - Generate embeddings for symptoms
   - Check cache (Redis)
   - Query vector database (Qdrant)

4. Diagnostic Engine
   - Multi-stage search
   - Calculate confidence scores
   - Apply clinical rules
   - Detect red flags

5. AI Enhancement (Optional)
   - Generate explanation
   - Create follow-up questions
   - Format medical report

6. Response
   - Aggregate results
   - Format response
   - Cache result
   - Return to client

7. Audit
   - Log request/response
   - Record in audit trail
   - Anonymize data
```

### Dataset Processing Flow

```
1. Download
   scripts/download_datasets/*.py
   - HPO from GitHub
   - ICD-10 from CDC
   - Sample datasets

2. Filter
   scripts/process_datasets/filter_*.py
   - Extract relevant conditions
   - Filter by symptom keywords
   - Remove administrative codes

3. Merge
   scripts/process_datasets/merge_all_datasets.py
   - Combine all datasets
   - Deduplicate
   - Unify schema

4. Embed
   src/services/embedding.py
   - Generate vectors for all conditions
   - Batch processing

5. Index
   scripts/process_datasets/index_in_qdrant.py
   - Create Qdrant collection
   - Upsert vectors with payloads
   - Build indexes
```

## Technology Stack

### Backend

- **Language**: Python 3.9+
- **Framework**: FastAPI 0.104+
- **ASGI Server**: Uvicorn
- **ML/NLP**:
  - Transformers (HuggingFace)
  - PyTorch
  - Sentence-transformers
  - spaCy (future NER)

### Databases

- **Vector Database**: Qdrant 1.7+
- **Relational Database**: PostgreSQL 14+
- **Cache**: Redis 7+

### ML Models

- **Primary**: `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext`
  - Type: BERT
  - Dimensions: 768
  - Domain: Biomedical literature

- **Alternative**: BioBERT
  - Similar architecture
  - Medical domain pre-training

- **AI Assistant**:
  - OpenAI GPT-4 Turbo
  - Or Llama2 (local, via Ollama)

### Infrastructure

- **Containerization**: Docker, Docker Compose
- **Deployment**: Docker, Kubernetes (future)
- **CI/CD**: GitHub Actions (future)
- **Monitoring**: Prometheus, Grafana (recommended)

## Database Schema

### Qdrant Collections

#### medical_conditions

```python
{
    "collection_name": "medical_conditions",
    "vectors": {
        "size": 768,
        "distance": "Cosine"
    },
    "payload_schema": {
        "condition_id": "string",       # Unique identifier
        "condition_name": "string",     # Display name
        "icd10_code": "string",         # ICD-10 code
        "category": "string",           # Disease category
        "common_symptoms": "string[]",  # Symptom list
        "rare_disease": "bool",         # Rare disease flag
        "severity": "string",           # low/moderate/high
        "source": "string",             # Data source (HPO/ICD10)
        "phenotypes": "string[]",       # HPO phenotype codes
        "genes": "string[]"             # Associated genes (HPO)
    }
}
```

### PostgreSQL Tables

#### cases

```sql
CREATE TABLE cases (
    case_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    patient_age INTEGER,
    patient_sex VARCHAR(10),
    chief_complaint TEXT,
    symptoms JSONB,
    metadata JSONB
);
```

#### diagnoses

```sql
CREATE TABLE diagnoses (
    diagnosis_id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(case_id),
    created_at TIMESTAMP DEFAULT NOW(),
    result JSONB,
    confidence FLOAT,
    review_tier VARCHAR(20),
    ai_enhanced BOOLEAN DEFAULT FALSE
);
```

#### audit_logs

```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    action VARCHAR(50),
    user_id UUID,
    case_id UUID,
    details JSONB,
    ip_address VARCHAR(45)
);
```

## API Design

### RESTful Endpoints

```
POST   /api/v1/analyze              # Analyze symptoms
POST   /api/v1/analyze/enhanced     # With AI enhancements
GET    /api/v1/condition/{id}       # Get condition details
POST   /api/v1/explain              # Simple explanations
POST   /api/v1/treatment-recommendations  # Treatment suggestions
GET    /api/v1/stats                # System statistics
GET    /health                      # Health check
GET    /docs                        # Swagger UI
GET    /redoc                       # ReDoc
```

### Request/Response Models

**Request Model:**

```python
class AnalysisRequest(BaseModel):
    case_id: str
    age: int = Field(..., ge=0, le=120)
    sex: Literal["male", "female", "other"]
    chief_complaint: str = Field(..., min_length=1)
    symptoms: List[Symptom]
    medical_history: Optional[List[str]] = []

class Symptom(BaseModel):
    description: str
    severity: Literal["mild", "moderate", "severe"]
    duration_days: int = Field(..., ge=0)
    frequency: str
```

**Response Model:**

```python
class DiagnosisResult(BaseModel):
    result_id: str
    case_id: str
    differential_diagnoses: List[Diagnosis]
    primary_diagnosis: Diagnosis
    review_tier: str
    overall_confidence: float
    red_flags_detected: List[str]
    requires_emergency_care: bool
    recommended_specialists: List[str]
    recommended_tests: List[str]
    reasoning_summary: str
    processing_time_ms: float
```

## Scalability

### Horizontal Scaling

**API Layer:**
- Stateless FastAPI instances
- Load balancer (Nginx, HAProxy)
- Session storage in Redis

**Database Layer:**
- Qdrant cluster (sharding)
- PostgreSQL read replicas
- Redis cluster

### Vertical Scaling

**GPU Acceleration:**
- CUDA-enabled embedding generation
- Batch processing optimization

**Memory Optimization:**
- Embedding cache in Redis
- Model quantization (future)

### Performance Targets

- **Query Latency**: <2s (p95)
- **Embedding Generation**: ~500ms
- **Vector Search**: <100ms
- **Throughput**: 100+ qps

### Caching Strategy

```
Level 1: Application Cache (in-memory)
  - Recently used embeddings
  - Hot path data

Level 2: Redis Cache (distributed)
  - Embedding vectors (1h TTL)
  - API responses (5m TTL)
  - Rate limit counters

Level 3: Database Cache
  - Qdrant internal caching
  - PostgreSQL query cache
```

## Security Architecture

### Authentication & Authorization

```
Client → API Key → Rate Limiter → Authorization → Service
```

**Layers:**
1. API Key validation
2. Rate limiting (Redis)
3. Role-based access control (RBAC)
4. Audit logging

### Data Security

- **In Transit**: TLS 1.3
- **At Rest**: Database encryption (future)
- **Anonymization**: PII removal
- **Audit Trail**: All operations logged

### HIPAA Compliance

- ✅ Access controls
- ✅ Audit logging
- ✅ Data anonymization
- ✅ Encryption support
- ✅ Session management

## Future Enhancements

### Planned Improvements

1. **Microservices Architecture**
   - Separate services for embedding, diagnosis, AI
   - Service mesh (Istio)
   - Distributed tracing

2. **Real-time Features**
   - WebSocket support
   - Streaming responses
   - Real-time collaboration

3. **Advanced ML**
   - Online learning
   - Federated learning
   - Explainable AI improvements

4. **Integration**
   - HL7 FHIR support
   - EHR integration
   - DICOM for imaging

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [BioBERT Paper](https://arxiv.org/abs/1901.08746)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)

---

**Last Updated**: 2025-11-14
