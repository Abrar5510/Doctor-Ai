"""
Tests for embedding service
"""

import pytest
import numpy as np
from src.services.embedding import EmbeddingService


@pytest.fixture
def embedding_service():
    """Create embedding service instance"""
    service = EmbeddingService()
    # Note: In real tests, you might want to use a smaller model or mock
    return service


def test_embedding_service_initialization(embedding_service):
    """Test that embedding service initializes correctly"""
    assert embedding_service is not None
    assert embedding_service.model is None  # Not initialized yet


def test_encode_single_text(embedding_service):
    """Test encoding a single text"""
    embedding_service.initialize()

    text = "Patient presents with fatigue and weight gain"
    embedding = embedding_service.encode(text)

    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 1
    assert embedding.shape[1] == embedding_service.settings.embedding_dimension


def test_encode_multiple_texts(embedding_service):
    """Test encoding multiple texts"""
    embedding_service.initialize()

    texts = [
        "Persistent fatigue",
        "Weight gain",
        "Cold intolerance"
    ]
    embeddings = embedding_service.encode(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] == embedding_service.settings.embedding_dimension


def test_encode_symptom_constellation(embedding_service):
    """Test encoding symptom constellation"""
    embedding_service.initialize()

    symptoms = [
        "Fatigue",
        "Weight gain",
        "Cold intolerance",
        "Dry skin"
    ]
    weights = [1.0, 1.0, 1.0, 0.5]

    embedding = embedding_service.encode_symptom_constellation(symptoms, weights)

    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[1] == embedding_service.settings.embedding_dimension


def test_compute_similarity(embedding_service):
    """Test similarity computation"""
    embedding_service.initialize()

    # Similar symptoms should have high similarity
    emb1 = embedding_service.encode("Persistent fatigue and weakness")
    emb2 = embedding_service.encode("Chronic fatigue and tiredness")

    similarity = embedding_service.compute_similarity(emb1, emb2)

    assert isinstance(similarity, float)
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.5  # Should be fairly similar
