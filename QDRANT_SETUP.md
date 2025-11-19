# Qdrant Cloud Setup Guide

## Overview

Doctor-AI uses **Qdrant Cloud** as the primary database for production deployments (Vercel, Railway, Render, etc.). This provides powerful semantic search capabilities using vector embeddings without requiring Docker or local infrastructure.

## Why Qdrant Cloud?

✅ **Serverless-Compatible** - Works perfectly with Vercel, Railway, Render
✅ **No Docker Required** - Pure cloud service, no containers needed
✅ **Free Tier Available** - 1GB free cluster for development
✅ **Automatic Backups** - Built-in data redundancy
✅ **Global CDN** - Low-latency access worldwide
✅ **Fully Managed** - No database maintenance required

## Quick Start (5 minutes)

### Step 1: Create Qdrant Cloud Account

1. Go to https://cloud.qdrant.io/
2. Sign up (free account, no credit card required)
3. Click **"Create Cluster"**
4. Choose:
   - **Free tier** (1GB storage)
   - **Region** closest to your users
   - **Cluster name** (e.g., "doctor-ai-prod")
5. Click **Create**

### Step 2: Get Your Credentials

Once your cluster is created:

1. Click on your cluster name
2. Copy the **Cluster URL** (e.g., `xxxxx.us-east-1.aws.cloud.qdrant.io`)
3. Go to **API Keys** tab
4. Click **Generate API Key**
5. Copy and save the API key securely

### Step 3: Configure Environment Variables

#### For Vercel:

1. Go to your Vercel project
2. Click **Settings** → **Environment Variables**
3. Add these variables:

```
PRIMARY_DATABASE=qdrant
QDRANT_HOST=xxxxx.us-east-1.aws.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your_api_key_here
QDRANT_COLLECTION_NAME=medical_conditions
```

#### For Local Development:

Create `.env` file:

```bash
PRIMARY_DATABASE=qdrant
QDRANT_HOST=xxxxx.us-east-1.aws.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your_api_key_here
QDRANT_COLLECTION_NAME=medical_conditions
SECRET_KEY=your_secret_key_at_least_32_chars_long
```

### Step 4: Load Data into Qdrant Cloud

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize and load all CSV data:

```bash
python scripts/init_qdrant.py
```

This will:
- ✅ Create 8 collections (users, patient_cases, medical_conditions, etc.)
- ✅ Load data from `/data/*.csv` files
- ✅ Generate AI embeddings for semantic search
- ✅ Upload everything to your Qdrant Cloud cluster

**Expected output:**
```
============================================================
Initializing Qdrant Collections
============================================================
Created collection: users
Created collection: user_sessions
Created collection: audit_logs
...
============================================================
Loading Data from CSV Files
============================================================
Loading users from data/users.csv...
  Uploaded 8 points to users
✓ users: 8 total points
...
============================================================
✓ Data Loading Complete!
============================================================
```

### Step 5: Verify Data

Check your Qdrant Cloud dashboard:

1. Go to https://cloud.qdrant.io/
2. Click on your cluster
3. Go to **Collections** tab
4. You should see 8 collections with data:
   - `medical_conditions` (15 points)
   - `patient_cases` (15 points)
   - `diagnosis_records` (20 points)
   - `users` (8 points)
   - `api_keys` (5 points)
   - `audit_logs` (15 points)
   - `user_sessions` (8 points)
   - `system_metrics` (20 points)

Or verify programmatically:

```python
from src.database.qdrant_manager import QdrantManager

manager = QdrantManager(
    host="xxxxx.us-east-1.aws.cloud.qdrant.io",
    port=6333,
    api_key="your_api_key"
)

for collection in ["medical_conditions", "patient_cases", "users"]:
    count = manager.count_points(collection)
    print(f"{collection}: {count} records")
```

## Data Structure

All application data is stored in CSV files in the `/data/` directory:

```
data/
├── medical_conditions.csv    # 15 medical conditions (heart attack, diabetes, etc.)
├── patient_cases.csv          # 15 sample patient cases
├── diagnosis_records.csv      # 20 diagnosis results
├── users.csv                  # 8 user accounts
├── api_keys.csv              # 5 API keys
├── audit_logs.csv            # 15 audit trail entries
├── user_sessions.csv         # 8 active sessions
└── system_metrics.csv        # 20 performance metrics
```

### Medical Conditions Dataset

15 common medical conditions with complete data:

1. **Acute Myocardial Infarction** (Heart Attack)
2. **Migraine with Aura**
3. **Lung Cancer**
4. **Rheumatoid Arthritis**
5. **Type 2 Diabetes Mellitus**
6. **Acute Appendicitis**
7. **Asthma**
8. **Congestive Heart Failure**
9. **Hypothyroidism**
10. **Alzheimer Disease**
11. **Acute Ischemic Stroke**
12. **Pneumonia**
13. **Urinary Tract Infection**
14. **Sepsis**
15. **Pulmonary Embolism**

Each condition includes:
- ✅ ICD-10 and SNOMED-CT codes
- ✅ Typical, rare, and red flag symptoms
- ✅ Diagnostic criteria
- ✅ Recommended tests and specialist referrals
- ✅ Age ranges and sex predilection
- ✅ Evidence sources and clinical guidelines

## Usage Examples

### Search Similar Medical Conditions

```python
from src.database.qdrant_manager import QdrantManager
from src.config import get_settings

settings = get_settings()
manager = QdrantManager(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    api_key=settings.qdrant_api_key,
)

# Find conditions matching symptoms
results = manager.search_similar(
    collection_name="medical_conditions",
    query_text="chest pain shortness of breath sweating",
    limit=5
)

for result in results:
    print(f"Match: {result['score']:.2%}")
    print(f"  Condition: {result['payload']['condition_name']}")
    print(f"  ICD-10: {result['payload']['icd10_code']}")
    print(f"  Urgency: {result['payload']['urgency_level']}")
    print()
```

### Get Specific Record

```python
# Get user by ID
user = manager.get_by_id("users", point_id=2)
print(f"Username: {user['payload']['username']}")
print(f"Role: {user['payload']['role']}")
```

### Update Data

```python
# Update user's last login
manager.update_payload(
    collection_name="users",
    point_id=2,
    payload={"last_login_at": "2024-01-20T10:00:00"}
)
```

### Filter and Count

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Count active users
active_count = manager.count_points(
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
print(f"Active users: {active_count}")
```

## Deployment to Vercel

### Environment Variables

In Vercel dashboard, add:

```
PRIMARY_DATABASE=qdrant
QDRANT_HOST=xxxxx.us-east-1.aws.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=<your_api_key>
SECRET_KEY=<generate_32_char_secret>
OPENAI_API_KEY=<your_openai_key>
```

### Build Configuration

Vercel automatically detects:
- **Frontend**: Vite build (React/Vue/Svelte)
- **Backend**: Python serverless functions in `/api`

No Docker needed! Everything runs serverless.

### First Deployment

1. Push your code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy!

Your app will use Qdrant Cloud automatically.

## Adding New Data

### Method 1: Update CSV and Reload

1. Edit CSV file in `/data/` directory
2. Run reload script:
```bash
python scripts/init_qdrant.py
```

### Method 2: Add Programmatically

```python
from src.database.qdrant_manager import QdrantManager
from qdrant_client.models import PointStruct

manager = QdrantManager(
    host="xxxxx.us-east-1.aws.cloud.qdrant.io",
    api_key="your_api_key"
)

# Generate embedding for new condition
condition_text = "Hypertension high blood pressure"
vector = manager.generate_embedding(condition_text)

# Create point
point = PointStruct(
    id=16,  # Next available ID
    vector=vector,
    payload={
        "id": 16,
        "condition_id": "COND016",
        "condition_name": "Hypertension",
        "icd_codes_json": '["I10"]',
        "typical_symptoms_json": '["headache", "dizziness", "chest pain"]',
        # ... more fields
    }
)

# Upload
manager.client.upsert(
    collection_name="medical_conditions",
    points=[point]
)
```

## Cost & Limits

### Qdrant Cloud Free Tier

- ✅ **1 GB storage** (enough for ~100,000+ medical records)
- ✅ **Unlimited queries**
- ✅ **All features included**
- ✅ **No credit card required**

Current usage (all 8 collections):
- ~106 total records
- ~50 MB storage (well within free tier)
- Room for 1000x growth

### Paid Tiers (if needed later)

- **$25/month**: 2 GB
- **$95/month**: 8 GB
- **Custom**: Enterprise features

## Local Development (Optional)

If you want to test locally with Docker before uploading to cloud:

```bash
# Start local Qdrant
docker-compose --profile local-dev up -d qdrant

# Update .env to use localhost
QDRANT_HOST=localhost
QDRANT_API_KEY=  # Leave empty

# Load data locally
python scripts/init_qdrant.py

# When ready, switch back to cloud and reload
QDRANT_HOST=xxxxx.us-east-1.aws.cloud.qdrant.io
QDRANT_API_KEY=your_api_key
python scripts/init_qdrant.py
```

## Troubleshooting

### "Connection refused" error

- ✅ Check `QDRANT_HOST` is correct (no `http://` or `https://`)
- ✅ Verify `QDRANT_API_KEY` is set
- ✅ Ensure cluster is running in Qdrant Cloud dashboard

### "Unauthorized" error

- ✅ API key is correct
- ✅ API key hasn't been revoked
- ✅ Regenerate key if needed

### Slow embedding generation

First run downloads BiomedNLP-PubMedBERT model (~400MB):
- Model cached in `~/.cache/huggingface/`
- Subsequent runs are much faster
- Consider using smaller model for faster processing

### Collection already exists

The `init_qdrant.py` script automatically recreates collections with `recreate=True`. Existing data will be replaced.

## Migration from PostgreSQL

If you have existing PostgreSQL data:

1. Export to CSV format
2. Place CSVs in `/data/` directory
3. Run `python scripts/init_qdrant.py`
4. Set `PRIMARY_DATABASE=qdrant` in environment
5. Deploy!

## Architecture Benefits

### vs PostgreSQL
- ✅ Semantic search (find similar symptoms, not just exact matches)
- ✅ No complex SQL queries needed
- ✅ Better for medical AI/ML applications
- ✅ Horizontally scalable

### vs Local Database
- ✅ Zero infrastructure management
- ✅ Automatic backups
- ✅ Global availability
- ✅ Perfect for serverless (Vercel, Railway, etc.)

## Resources

- **Qdrant Cloud**: https://cloud.qdrant.io/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **BiomedNLP Model**: https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
- **Architecture**: See `QDRANT_ARCHITECTURE.md`
- **Sample Data**: See `/data/` directory

## Support

Questions? Check:
1. Qdrant Cloud dashboard for cluster status
2. CSV files in `/data/` for data integrity
3. Environment variables are set correctly
4. `QDRANT_ARCHITECTURE.md` for technical details

**You're all set!** 🎉 Your database is cloud-hosted, version-controlled (CSV), and ready for production.
