# Qdrant Database Setup Guide

## Overview

Doctor-AI now uses **Qdrant as the primary database**, replacing PostgreSQL. This provides powerful semantic search capabilities using vector embeddings generated from medical text.

## Architecture

### What Changed?

- **Before**: PostgreSQL relational database
- **Now**: Qdrant vector database with semantic search
- **Data**: All application data stored in CSV files (`/data/`) and loaded into Qdrant

### Benefits

1. **Semantic Search**: Find similar medical conditions using AI embeddings
2. **Flexible Schema**: Easy to add new fields without migrations
3. **Performance**: Fast vector similarity search for diagnosis matching
4. **Scalability**: Horizontal scaling for large medical datasets
5. **CSV-Based**: All data is version-controlled in CSV format

## Quick Start

### 1. Start Qdrant with Docker

```bash
# Start Qdrant (and Redis)
docker-compose up -d qdrant redis

# Verify Qdrant is running
curl http://localhost:6333/
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Qdrant Database

```bash
# Load all CSV data into Qdrant collections
python scripts/init_qdrant.py
```

This will:
- Create 8 Qdrant collections (users, patient_cases, medical_conditions, etc.)
- Load data from CSV files in `/data/`
- Generate embeddings using BiomedNLP-PubMedBERT model
- Insert all data with vectors into Qdrant

### 4. Verify Data Loaded

```bash
# Check Qdrant dashboard
open http://localhost:6333/dashboard

# Or use Python to check:
python -c "
from src.database.qdrant_manager import QdrantManager
manager = QdrantManager()
print('Collections:')
for col in ['users', 'patient_cases', 'medical_conditions', 'diagnosis_records']:
    count = manager.count_points(col)
    print(f'  {col}: {count} points')
"
```

## Data Structure

### CSV Files in `/data/`

All application data is stored in CSV files for easy version control:

```
data/
├── medical_conditions.csv    # Medical knowledge base (15 conditions)
├── patient_cases.csv          # Patient case records (15 cases)
├── diagnosis_records.csv      # Diagnosis results (20 diagnoses)
├── users.csv                  # User accounts (8 users)
├── api_keys.csv              # API keys (5 keys)
├── audit_logs.csv            # Audit trail (15 logs)
├── user_sessions.csv         # Active sessions (8 sessions)
└── system_metrics.csv        # Performance metrics (20 metrics)
```

### Qdrant Collections

Each CSV file maps to a Qdrant collection:

| Collection | CSV File | Vector Fields | Points |
|------------|----------|---------------|--------|
| medical_conditions | medical_conditions.csv | condition_name + symptoms | 15 |
| patient_cases | patient_cases.csv | chief_complaint + symptoms | 15 |
| diagnosis_records | diagnosis_records.csv | condition_name + matching_symptoms | 20 |
| users | users.csv | username + full_name + role | 8 |
| api_keys | api_keys.csv | name + description | 5 |
| audit_logs | audit_logs.csv | action + description | 15 |
| user_sessions | user_sessions.csv | user_agent + device_info | 8 |
| system_metrics | system_metrics.csv | metric_type + metric_name | 20 |

## Configuration

### Environment Variables

Update your `.env` file:

```bash
# Primary Database Configuration
PRIMARY_DATABASE=qdrant  # Use "qdrant" or "postgresql"

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=  # Optional, leave empty for local development

# ML Model for Embeddings
EMBEDDING_MODEL=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
EMBEDDING_DIMENSION=768
```

### Docker Compose Profiles

```bash
# Default: Qdrant + Redis (recommended)
docker-compose up -d

# With PostgreSQL (legacy mode)
docker-compose --profile legacy up -d

# Full stack (API + all databases)
docker-compose --profile full up -d
```

## Usage Examples

### Python API

```python
from src.database.qdrant_manager import QdrantManager

# Initialize manager
manager = QdrantManager(
    host="localhost",
    port=6333,
    vector_size=768
)

# Search for similar medical conditions
results = manager.search_similar(
    collection_name="medical_conditions",
    query_text="chest pain shortness of breath sweating",
    limit=5
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Condition: {result['payload']['condition_name']}")
    print(f"ICD-10: {result['payload']['icd10_code']}")
    print()

# Get specific record by ID
user = manager.get_by_id("users", point_id=2)
print(f"User: {user['payload']['username']}")

# Update data
manager.update_payload(
    collection_name="users",
    point_id=2,
    payload={"last_login_at": "2024-01-20 10:00:00"}
)

# Count records with filters
from qdrant_client.models import Filter, FieldCondition, MatchValue

active_users = manager.count_points(
    collection_name="users",
    filters=Filter(
        must=[
            FieldCondition(
                key="is_active",
                match=MatchValue(value=True)
            )
        ]
    )
)
print(f"Active users: {active_users}")
```

### Adding New Data

1. **Update CSV file** in `/data/` directory
2. **Reload data**:
```bash
python scripts/init_qdrant.py
```

Or reload specific collection:
```python
from src.database.qdrant_manager import QdrantManager

manager = QdrantManager()
manager.load_csv_to_collection(
    collection_name="medical_conditions",
    csv_path="data/medical_conditions.csv",
    embedding_fields=["condition_name", "typical_symptoms_json", "rare_symptoms_json"]
)
```

## Medical Conditions Dataset

The `/data/medical_conditions.csv` contains 15 common medical conditions:

1. Acute Myocardial Infarction (Heart Attack)
2. Migraine with Aura
3. Lung Cancer
4. Rheumatoid Arthritis
5. Type 2 Diabetes Mellitus
6. Acute Appendicitis
7. Asthma
8. Congestive Heart Failure
9. Hypothyroidism
10. Alzheimer Disease
11. Acute Ischemic Stroke
12. Pneumonia
13. Urinary Tract Infection
14. Sepsis
15. Pulmonary Embolism

Each condition includes:
- ICD-10 and SNOMED codes
- Typical and rare symptoms
- Red flag symptoms
- Diagnostic criteria
- Recommended tests
- Specialist referrals
- Clinical evidence sources

## Troubleshooting

### Qdrant not starting

```bash
# Check Qdrant logs
docker logs doctor-ai-qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### Embeddings generation slow

The first time you run `init_qdrant.py`, it will download the BiomedNLP-PubMedBERT model (~400MB). Subsequent runs will be faster.

```bash
# Model is cached in:
~/.cache/huggingface/transformers/
```

### Collection already exists error

```bash
# Recreate collections (WARNING: deletes existing data)
python scripts/init_qdrant.py
```

The script automatically recreates collections with `recreate=True`.

### Port 6333 already in use

```bash
# Stop existing Qdrant instance
docker stop $(docker ps -q --filter ancestor=qdrant/qdrant)

# Or change port in docker-compose.yml
```

## Migration from PostgreSQL

If you have existing PostgreSQL data:

1. **Export data to CSV** using `scripts/export_postgres_to_csv.py` (create if needed)
2. **Place CSVs in `/data/` directory**
3. **Run initialization**: `python scripts/init_qdrant.py`
4. **Update config**: Set `PRIMARY_DATABASE=qdrant` in `.env`
5. **Test thoroughly** before decommissioning PostgreSQL

## Performance

### Benchmarks (on sample data)

- **Embedding generation**: ~500ms per text (using BiomedNLP-PubMedBERT)
- **Vector search**: ~50-200ms for 1000+ points
- **Batch upload**: ~100 points per second
- **Collection initialization**: ~2-5 minutes (including embeddings)

### Optimization Tips

1. **Batch operations**: Upload in batches of 100 points
2. **Cache embeddings**: Store pre-computed embeddings when possible
3. **Use filters**: Combine vector search with payload filters for precision
4. **Index tuning**: Adjust HNSW parameters for your use case

## API Endpoints

Update your FastAPI routes to use Qdrant:

```python
from src.database.qdrant_manager import QdrantManager
from src.config import settings

# Initialize once (e.g., in startup event)
qdrant_manager = QdrantManager(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    api_key=settings.qdrant_api_key,
)

@app.get("/diagnose")
async def diagnose(symptoms: str):
    # Search medical conditions by symptom similarity
    results = qdrant_manager.search_similar(
        collection_name="medical_conditions",
        query_text=symptoms,
        limit=10
    )
    return {"diagnoses": results}
```

## Resources

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **BiomedNLP-PubMedBERT**: https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
- **Architecture Doc**: See `QDRANT_ARCHITECTURE.md`
- **Sample Data**: See `/data/` directory

## Support

For issues or questions:
1. Check Qdrant logs: `docker logs doctor-ai-qdrant`
2. Verify CSV data: `ls -lh data/`
3. Test connection: `curl http://localhost:6333/collections`
4. Review architecture: `QDRANT_ARCHITECTURE.md`
