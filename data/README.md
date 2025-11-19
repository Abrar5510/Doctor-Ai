# Doctor-AI Database - CSV Data Files

This directory contains application data in CSV format that is loaded into Qdrant Cloud.

## Files

| File | Records | Description |
|------|---------|-------------|
| `medical_conditions.csv` | 15 | Medical conditions with symptoms and ICD-10 codes |
| `patient_cases.csv` | 15 | Sample patient case records |
| `diagnosis_records.csv` | 20 | Diagnosis results with confidence scores |
| `users.csv` | 8 | User accounts |
| `api_keys.csv` | 5 | API keys for authentication |
| `audit_logs.csv` | 15 | HIPAA-compliant audit trail |
| `user_sessions.csv` | 8 | Active user sessions |
| `system_metrics.csv` | 20 | Performance metrics |

## Loading Data

```bash
# Load all CSV data into Qdrant
python scripts/init_qdrant.py
```

This will:
1. Create Qdrant collections
2. Generate embeddings using BiomedNLP-PubMedBERT
3. Upload all data to Qdrant Cloud

## Modifying Data

### Edit CSV Files

1. Edit the CSV file directly
2. Reload: `python scripts/init_qdrant.py`

### Programmatic Updates

```python
from src.database.qdrant_manager import QdrantManager

manager = QdrantManager()
manager.update_payload(
    collection_name="users",
    point_id=2,
    payload={"last_login_at": "2024-01-20T10:00:00"}
)
```

## Data Integrity

- Version controlled via Git
- Human-readable CSV format
- Easy to backup and restore
- Portable across environments
