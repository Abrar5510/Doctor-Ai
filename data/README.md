# Doctor-AI Database - CSV Data Files

This directory contains all application data in CSV format. These files serve as the source of truth and are loaded into Qdrant Cloud for production use.

## Files Overview

| File | Records | Description |
|------|---------|-------------|
| `medical_conditions.csv` | 15 | Medical knowledge base with symptoms, ICD-10 codes, diagnostic criteria |
| `patient_cases.csv` | 15 | Sample patient case records with demographics and symptoms |
| `diagnosis_records.csv` | 20 | Diagnosis results with confidence scores and clinical evidence |
| `users.csv` | 8 | User accounts with roles and authentication data |
| `api_keys.csv` | 5 | API keys for service-to-service authentication |
| `audit_logs.csv` | 15 | HIPAA-compliant audit trail entries |
| `user_sessions.csv` | 8 | Active user sessions with JWT tokens |
| `system_metrics.csv` | 20 | Performance and usage metrics |

## Loading Data into Qdrant

To load all CSV data into your Qdrant Cloud cluster:

```bash
# Ensure environment variables are set
# QDRANT_HOST, QDRANT_API_KEY, etc.

# Run initialization script
python scripts/init_qdrant.py
```

This will:
1. Create 8 Qdrant collections
2. Generate embeddings using BiomedNLP-PubMedBERT
3. Upload all data to Qdrant Cloud

## Data Structure

### medical_conditions.csv
Medical knowledge base with 15 common conditions:
- Acute Myocardial Infarction, Migraine with Aura, Lung Cancer, Rheumatoid Arthritis, Type 2 Diabetes, Acute Appendicitis, Asthma, Congestive Heart Failure, Hypothyroidism, Alzheimer Disease, Acute Ischemic Stroke, Pneumonia, UTI, Sepsis, Pulmonary Embolism

Fields:
- `condition_id`, `condition_name`, `icd_codes_json`, `snomed_codes_json`
- `typical_symptoms_json`, `rare_symptoms_json`, `red_flag_symptoms_json`
- `diagnostic_criteria_json`, `recommended_tests_json`
- `specialist_referral`, `urgency_level`, `prevalence`
- `typical_age_range`, `sex_predilection`

### patient_cases.csv
Sample patient cases with realistic medical scenarios:
- Various ages, sexes, ethnicities, locations
- Chief complaints and symptom presentations
- Medical history and family history
- Diagnosis results and review tiers

### diagnosis_records.csv
Differential diagnosis results:
- Linked to patient cases
- ICD-10 and SNOMED codes
- Similarity and confidence scores
- Matching symptoms and supporting evidence
- Physician confirmation and notes

### users.csv
User accounts with different roles:
- Admins, Physicians, Nurses, Researchers, API Users
- Authentication data (hashed passwords)
- Security fields (failed login attempts, verification tokens)
- Audit timestamps

### api_keys.csv
API keys for programmatic access:
- Key hashes and prefixes
- Scopes and rate limits
- Usage tracking
- Expiration dates

### audit_logs.csv
HIPAA-compliant audit trail:
- User actions (login, create_case, run_diagnosis, etc.)
- Resource types and IDs
- Request metadata (IP, user agent, method, path)
- Timestamps and duration

### user_sessions.csv
Active user sessions:
- JWT token IDs
- Session metadata (IP address, user agent, device info)
- Lifecycle timestamps (created, expires, last_activity)
- Revocation status

### system_metrics.csv
Performance and usage metrics:
- Query latencies, embedding times, cache hit rates
- Database query times
- API request counts
- Endpoint-specific metrics

## Modifying Data

### Option 1: Edit CSV Directly

1. Edit the CSV file
2. Reload data: `python scripts/init_qdrant.py`

### Option 2: Programmatic Updates

```python
from src.database.qdrant_manager import QdrantManager

manager = QdrantManager()
manager.update_payload(
    collection_name="users",
    point_id=2,
    payload={"last_login_at": "2024-01-20T10:00:00"}
)
```

### Option 3: Add New Records

Add rows to CSV, then reload, or use Python:

```python
from qdrant_client.models import PointStruct

vector = manager.generate_embedding("new condition text")
point = PointStruct(id=16, vector=vector, payload={...})
manager.client.upsert(collection_name="medical_conditions", points=[point])
```

## Data Integrity

- ✅ **Version controlled** via Git
- ✅ **Human-readable** CSV format
- ✅ **Easy to backup** and restore
- ✅ **Portable** across environments
- ✅ **Auditable** changes in Git history

## Usage in Application

The application uses `QdrantManager` to:
- Load CSV data into vector collections
- Perform semantic similarity searches
- Filter and retrieve records
- Update payloads in real-time

See `QDRANT_SETUP.md` for complete setup instructions.
