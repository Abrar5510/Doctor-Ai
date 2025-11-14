# Testing Guide

This document provides comprehensive testing guidelines for the Doctor-AI project.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Medical Data Testing](#medical-data-testing)
- [API Testing](#api-testing)
- [Performance Testing](#performance-testing)
- [Integration Testing](#integration-testing)
- [CI/CD Testing](#cicd-testing)

## Testing Philosophy

### Principles

1. **Test What Matters**: Focus on critical paths and edge cases
2. **Fast Feedback**: Tests should run quickly
3. **Reliable**: Tests should be deterministic and reproducible
4. **Maintainable**: Tests should be easy to understand and update
5. **Medical Accuracy**: Validate clinical correctness

### Testing Pyramid

```
         ┌─────────────┐
         │   Manual    │  5%  - Manual exploratory testing
         └─────────────┘
        ┌───────────────┐
        │  Integration  │  15% - Service integration tests
        └───────────────┘
      ┌───────────────────┐
      │   Component/API   │  30% - API and component tests
      └───────────────────┘
    ┌───────────────────────┐
    │       Unit Tests      │  50% - Unit tests
    └───────────────────────┘
```

## Test Types

### 1. Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Location**: `tests/test_*.py`

**Example**:

```python
# tests/test_embedding.py
import pytest
from src.services.embedding import EmbeddingService

class TestEmbeddingService:
    @pytest.fixture
    def embedding_service(self):
        return EmbeddingService()

    def test_generate_embedding(self, embedding_service):
        """Test embedding generation for simple text."""
        text = "fever and cough"
        embedding = embedding_service.generate_embedding(text)

        assert embedding is not None
        assert len(embedding) == 768  # PubMedBERT dimension
        assert all(isinstance(x, float) for x in embedding)

    def test_empty_text_raises_error(self, embedding_service):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embedding_service.generate_embedding("")

    def test_batch_embedding(self, embedding_service):
        """Test batch embedding generation."""
        texts = ["fever", "cough", "fatigue"]
        embeddings = embedding_service.generate_batch_embeddings(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 768 for emb in embeddings)
```

### 2. Integration Tests

**Purpose**: Test interaction between multiple components

**Example**:

```python
# tests/test_integration.py
import pytest
from src.services.diagnostic import DiagnosticService
from src.services.vector_store import VectorStoreService
from src.services.embedding import EmbeddingService

class TestDiagnosticIntegration:
    @pytest.fixture
    async def services(self):
        embedding = EmbeddingService()
        vector_store = VectorStoreService()
        diagnostic = DiagnosticService(embedding, vector_store)
        return diagnostic

    @pytest.mark.asyncio
    async def test_end_to_end_diagnosis(self, services):
        """Test complete diagnosis flow."""
        symptoms = [
            {"description": "high fever", "severity": "high"},
            {"description": "dry cough", "severity": "moderate"}
        ]

        result = await services.analyze(symptoms, age=35, sex="female")

        assert result is not None
        assert len(result.differential_diagnoses) > 0
        assert result.overall_confidence > 0
        assert result.review_tier in ["tier1", "tier2", "tier3", "tier4"]
```

### 3. API Tests

**Purpose**: Test REST API endpoints

**Location**: `tests/test_api/`

**Example**:

```python
# tests/test_api/test_routes.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAnalyzeEndpoint:
    def test_analyze_valid_request(self):
        """Test successful symptom analysis."""
        request = {
            "case_id": "test_001",
            "age": 35,
            "sex": "female",
            "chief_complaint": "Fever and cough",
            "symptoms": [
                {
                    "description": "High fever",
                    "severity": "high",
                    "duration_days": 3,
                    "frequency": "constant"
                }
            ]
        }

        response = client.post("/api/v1/analyze", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "primary_diagnosis" in data
        assert "differential_diagnoses" in data
        assert "overall_confidence" in data

    def test_analyze_invalid_age(self):
        """Test validation for invalid age."""
        request = {
            "case_id": "test_002",
            "age": -5,  # Invalid
            "sex": "female",
            "chief_complaint": "Fever",
            "symptoms": [{"description": "fever"}]
        }

        response = client.post("/api/v1/analyze", json=request)

        assert response.status_code == 422  # Validation error

    def test_analyze_empty_symptoms(self):
        """Test error handling for empty symptoms."""
        request = {
            "case_id": "test_003",
            "age": 35,
            "sex": "female",
            "chief_complaint": "Fever",
            "symptoms": []  # Empty
        }

        response = client.post("/api/v1/analyze", json=request)

        assert response.status_code == 400  # Bad request
```

### 4. Performance Tests

**Purpose**: Measure and validate performance metrics

**Example**:

```python
# tests/test_performance.py
import pytest
import time
from src.services.embedding import EmbeddingService

class TestPerformance:
    @pytest.fixture
    def embedding_service(self):
        return EmbeddingService()

    def test_embedding_generation_speed(self, embedding_service):
        """Test embedding generation meets performance target."""
        text = "fever, cough, fatigue, headache, body aches"

        start = time.time()
        embedding = embedding_service.generate_embedding(text)
        duration = time.time() - start

        assert duration < 0.5  # Should be under 500ms
        assert embedding is not None

    @pytest.mark.parametrize("batch_size", [1, 10, 50, 100])
    def test_batch_processing_scaling(self, embedding_service, batch_size):
        """Test batch processing scales linearly."""
        texts = ["symptom text"] * batch_size

        start = time.time()
        embeddings = embedding_service.generate_batch_embeddings(texts)
        duration = time.time() - start

        # Batching should be more efficient than sequential
        per_item_time = duration / batch_size
        assert per_item_time < 0.5  # Average under 500ms per item
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_embedding.py

# Run specific test class
pytest tests/test_embedding.py::TestEmbeddingService

# Run specific test method
pytest tests/test_embedding.py::TestEmbeddingService::test_generate_embedding

# Run tests matching pattern
pytest -k "embedding"
```

### With Coverage

```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

### Continuous Testing

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw -- -v
```

## Writing Tests

### Test Structure

Follow the **AAA pattern** (Arrange, Act, Assert):

```python
def test_example():
    # Arrange: Set up test data and dependencies
    service = MyService()
    input_data = {"key": "value"}

    # Act: Execute the code under test
    result = service.process(input_data)

    # Assert: Verify the results
    assert result is not None
    assert result.status == "success"
```

### Fixtures

Use pytest fixtures for reusable test setup:

```python
import pytest

@pytest.fixture
def sample_symptoms():
    """Provide sample symptom data for tests."""
    return [
        {"description": "fever", "severity": "high"},
        {"description": "cough", "severity": "moderate"}
    ]

@pytest.fixture
async def diagnostic_service():
    """Provide configured diagnostic service."""
    service = DiagnosticService()
    await service.initialize()
    yield service
    await service.cleanup()

def test_with_fixtures(sample_symptoms, diagnostic_service):
    """Test using multiple fixtures."""
    result = diagnostic_service.analyze(sample_symptoms)
    assert result is not None
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("age,sex,expected_tier", [
    (5, "male", "tier2"),      # Child
    (35, "female", "tier1"),   # Adult
    (75, "male", "tier3"),     # Elderly
])
def test_age_based_triage(age, sex, expected_tier):
    """Test triage logic for different age groups."""
    result = calculate_triage(age=age, sex=sex)
    assert result.tier == expected_tier
```

### Async Tests

Test asynchronous code:

```python
import pytest

@pytest.mark.asyncio
async def test_async_diagnosis():
    """Test async diagnosis function."""
    service = DiagnosticService()
    symptoms = [{"description": "fever"}]

    result = await service.analyze_async(symptoms)

    assert result is not None
```

### Mocking

Use mocks for external dependencies:

```python
from unittest.mock import Mock, patch

def test_with_mocked_llm():
    """Test AI assistant with mocked LLM."""
    with patch('src.services.ai_assistant.OpenAI') as mock_openai:
        # Configure mock
        mock_openai.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mocked response"))]
        )

        # Test
        assistant = AIAssistant()
        response = assistant.generate_explanation("diagnosis")

        assert response == "Mocked response"
        mock_openai.return_value.chat.completions.create.assert_called_once()
```

## Test Coverage

### Coverage Goals

- **Overall**: 80%+ coverage
- **Critical Paths**: 95%+ coverage
- **New Code**: 90%+ coverage

### Measuring Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing tests/

# Coverage breakdown by file
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

### Coverage Report

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/__init__.py                      2      0   100%
src/services/embedding.py          150     15    90%   45-50, 120
src/services/diagnostic.py         200     30    85%   78-85, 150-160
src/services/vector_store.py       100      5    95%   88-90
src/api/routes.py                  120     20    83%   45-55, 90-95
---------------------------------------------------------------
TOTAL                              572     70    88%
```

### Exclude from Coverage

```python
# .coveragerc
[run]
omit =
    tests/*
    */__init__.py
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

## Medical Data Testing

### Synthetic Test Data

**NEVER** use real patient data. Use synthetic data:

```python
# tests/fixtures/medical_data.py

SYNTHETIC_CASES = [
    {
        "case_id": "synth_001",
        "age": 35,
        "sex": "female",
        "symptoms": [
            {"description": "fatigue", "duration_days": 60},
            {"description": "weight gain", "duration_days": 90},
            {"description": "cold intolerance", "duration_days": 60}
        ],
        "expected_diagnosis": "Hypothyroidism",
        "expected_confidence_range": (0.75, 0.95)
    },
    # More synthetic cases...
]

@pytest.fixture
def synthetic_cases():
    return SYNTHETIC_CASES
```

### Clinical Validation

Validate medical accuracy:

```python
def test_hypothyroidism_detection():
    """Test detection of classic hypothyroidism presentation."""
    symptoms = [
        {"description": "fatigue", "severity": "moderate"},
        {"description": "weight gain", "severity": "moderate"},
        {"description": "cold intolerance", "severity": "mild"},
        {"description": "constipation", "severity": "mild"}
    ]

    result = diagnostic_service.analyze(symptoms)

    # Verify hypothyroidism is in top 3 diagnoses
    top_3 = [d.condition_name for d in result.differential_diagnoses[:3]]
    assert "Hypothyroidism" in top_3

    # Verify confidence is reasonable
    hypo_diagnosis = next(
        d for d in result.differential_diagnoses
        if d.condition_name == "Hypothyroidism"
    )
    assert hypo_diagnosis.confidence > 0.6
```

### Edge Cases

Test rare and edge cases:

```python
@pytest.mark.parametrize("case", [
    # Ultra-rare disease
    {"symptoms": ["fever", "rash", "joint pain"], "rare": True},
    # Vague symptoms
    {"symptoms": ["fatigue"], "vague": True},
    # Conflicting symptoms
    {"symptoms": ["fever", "hypothermia"], "conflicting": True},
    # Large symptom list
    {"symptoms": ["symptom_" + str(i) for i in range(50)], "many": True}
])
def test_edge_cases(case):
    """Test handling of edge cases."""
    result = diagnostic_service.analyze(case["symptoms"])
    assert result is not None
```

## API Testing

### Manual API Testing

Using scripts:

```bash
# Test basic analysis
python scripts/test_api.py

# Test AI assistant features
python scripts/test_ai_assistant.py

# Test Qdrant connection
python scripts/test_qdrant_connection.py
```

### Automated API Testing

Using pytest:

```python
def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stats_endpoint():
    """Test stats endpoint."""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_conditions" in data
    assert "vector_count" in data
```

### Load Testing

Using Locust:

```python
# locustfile.py
from locust import HttpUser, task, between

class DoctorAIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze_symptoms(self):
        self.client.post("/api/v1/analyze", json={
            "case_id": "load_test",
            "age": 35,
            "sex": "female",
            "chief_complaint": "Fever",
            "symptoms": [
                {"description": "fever", "severity": "high"}
            ]
        })
```

Run load test:

```bash
locust -f locustfile.py --host http://localhost:8000
```

## Performance Testing

### Benchmarking

```python
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

def test_embedding_performance(benchmark: BenchmarkFixture):
    """Benchmark embedding generation."""
    service = EmbeddingService()
    text = "fever, cough, fatigue"

    result = benchmark(service.generate_embedding, text)

    assert result is not None
```

### Profiling

```bash
# Install profiling tools
pip install line_profiler memory_profiler

# Profile a function
python -m line_profiler script.py

# Memory profiling
python -m memory_profiler script.py
```

## Integration Testing

### Database Integration

```python
@pytest.mark.integration
async def test_vector_store_integration():
    """Test integration with Qdrant."""
    vector_store = VectorStoreService()

    # Create test collection
    await vector_store.create_collection("test_collection", vector_size=768)

    # Insert test data
    test_point = {
        "id": "test_1",
        "vector": [0.1] * 768,
        "payload": {"name": "test"}
    }
    await vector_store.upsert("test_collection", [test_point])

    # Search
    results = await vector_store.search(
        collection_name="test_collection",
        query_vector=[0.1] * 768,
        limit=1
    )

    assert len(results) == 1
    assert results[0].id == "test_1"
```

### External API Integration

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
def test_openai_integration():
    """Test integration with OpenAI API."""
    assistant = AIAssistant()
    response = assistant.generate_explanation("Test diagnosis")

    assert response is not None
    assert len(response) > 0
```

## CI/CD Testing

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=src tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is tested
2. **One Assertion**: Prefer one logical assertion per test
3. **Independent**: Tests should not depend on each other
4. **Fast**: Keep tests fast (<1s per unit test)
5. **Deterministic**: No random failures
6. **Clean Up**: Always clean up resources
7. **Document**: Add docstrings explaining complex tests

## Troubleshooting

### Tests Fail Locally

```bash
# Clean pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Qdrant is running
curl http://localhost:6333/health
```

### Slow Tests

```bash
# Identify slow tests
pytest --durations=10

# Run only fast tests
pytest -m "not slow"
```

---

**Last Updated**: 2025-11-14
