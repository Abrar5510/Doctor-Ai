# Quick Start Guide 🚀

Get the Medical Symptom Constellation Mapper running in under 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Docker and Docker Compose installed
- 8GB+ RAM
- Internet connection (for downloading models)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/Abrar5510/Doctor-Ai.git
cd Doctor-Ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 5. Start Database Services

```bash
docker-compose up -d
```

This starts:
- ✅ Qdrant (Vector Database) on port 6333
- ✅ PostgreSQL on port 5432
- ✅ Redis on port 6379

### 6. Seed the Database

```bash
python scripts/seed_data.py
```

This will:
- Download the PubMedBERT model (~420MB)
- Generate embeddings for 8 sample medical conditions
- Insert them into Qdrant

**Note**: First run takes 5-10 minutes due to model download. Be patient! ☕

### 7. Start the API Server

```bash
python -m src.main
```

Or use the Makefile:

```bash
make start
```

### 8. Test the API

Open a new terminal and run:

```bash
python scripts/test_api.py
```

Or visit the interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick Test Example

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "test_001",
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
        "description": "Weight gain of 15 pounds",
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
  }'
```

### Using Python

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/analyze",
            json={
                "case_id": "test_001",
                "age": 35,
                "sex": "female",
                "chief_complaint": "Persistent fatigue and weight gain",
                "symptoms": [
                    {
                        "description": "Extreme fatigue for 2 months",
                        "severity": "moderate",
                        "duration_days": 60,
                        "frequency": "constant"
                    }
                ]
            }
        )
        result = response.json()
        print(f"Primary Diagnosis: {result['primary_diagnosis']['condition_name']}")
        print(f"Confidence: {result['overall_confidence']:.2%}")

asyncio.run(test())
```

## Expected Output

You should see a diagnostic result like:

```json
{
  "primary_diagnosis": {
    "condition_name": "Hypothyroidism",
    "confidence_score": 0.88
  },
  "review_tier": "tier1_automated",
  "overall_confidence": 0.88,
  "differential_diagnoses": [
    {
      "condition_name": "Hypothyroidism",
      "confidence_score": 0.88,
      "recommended_next_steps": ["TSH", "Free T4", "TPO antibodies"]
    }
  ]
}
```

## Troubleshooting

### Model Download Fails

If the PubMedBERT model download fails:
1. Check internet connection
2. Try again (downloads resume automatically)
3. Or use a smaller model by editing `.env`:
   ```
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384
   ```

### Docker Ports Already in Use

If ports are already taken:
1. Edit `docker-compose.yml` to use different ports
2. Update `.env` with new port numbers

### Out of Memory

If you run out of memory:
1. Close other applications
2. Use CPU instead of GPU (automatic fallback)
3. Reduce batch size in embedding service

## Makefile Commands

```bash
make help          # Show all available commands
make setup         # Complete setup (install + docker + seed)
make start         # Start all services
make stop          # Stop all services
make test          # Run tests
make test-api      # Test API endpoints
make clean         # Clean up generated files
make docs          # Open API documentation
```

## Next Steps

1. ✅ Explore the API documentation at http://localhost:8000/docs
2. ✅ Try different symptom combinations
3. ✅ Add more medical conditions to the database
4. ✅ Customize confidence thresholds in `.env`
5. ✅ Read the full README.md for advanced usage

## Support

- **Issues**: https://github.com/Abrar5510/Doctor-Ai/issues
- **Documentation**: README.md
- **API Docs**: http://localhost:8000/docs

---

**Happy diagnosing! 🏥**
