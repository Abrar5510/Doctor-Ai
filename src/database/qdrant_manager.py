"""
Qdrant Database Manager for Doctor-AI Application.

This module provides functionality to interact with Qdrant vector database
as the primary data store, replacing PostgreSQL.
"""

import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
from transformers import AutoTokenizer, AutoModel
import torch


class QdrantManager:
    """Manager class for Qdrant database operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        embedding_model: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext",
        vector_size: int = 768,
    ):
        """Initialize Qdrant client and embedding model."""
        self.client = QdrantClient(host=host, port=port, api_key=api_key)
        self.vector_size = vector_size

        # Initialize embedding model
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.model = AutoModel.from_pretrained(embedding_model)
        self.model.eval()  # Set to evaluation mode

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text using BiomedNLP-PubMedBERT."""
        # Tokenize and encode
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling
            embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings[0].tolist()

    def create_collection(self, collection_name: str, recreate: bool = False):
        """Create a Qdrant collection with vector configuration."""
        if recreate and self.client.collection_exists(collection_name):
            self.client.delete_collection(collection_name)
            print(f"Deleted existing collection: {collection_name}")

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection already exists: {collection_name}")

    def initialize_all_collections(self, recreate: bool = False):
        """Initialize all required collections for Doctor-AI."""
        collections = [
            "users",
            "user_sessions",
            "audit_logs",
            "api_keys",
            "patient_cases",
            "diagnosis_records",
            "system_metrics",
            "medical_conditions",
        ]

        for collection in collections:
            self.create_collection(collection, recreate=recreate)

    def load_csv_to_collection(
        self,
        collection_name: str,
        csv_path: str,
        embedding_fields: List[str],
        id_field: str = "id",
    ):
        """
        Load data from CSV file into Qdrant collection.

        Args:
            collection_name: Name of the collection
            csv_path: Path to CSV file
            embedding_fields: List of fields to use for generating embeddings
            id_field: Field to use as point ID
        """
        print(f"\nLoading {collection_name} from {csv_path}...")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            points = []

            for row in reader:
                # Generate embedding text from specified fields
                embedding_text_parts = []
                for field in embedding_fields:
                    if row.get(field):
                        # Handle JSON fields
                        if field.endswith('_json'):
                            try:
                                json_data = json.loads(row[field])
                                if isinstance(json_data, list):
                                    embedding_text_parts.extend([str(item) for item in json_data])
                                else:
                                    embedding_text_parts.append(str(json_data))
                            except json.JSONDecodeError:
                                embedding_text_parts.append(row[field])
                        else:
                            embedding_text_parts.append(row[field])

                embedding_text = " ".join(embedding_text_parts)
                vector = self.generate_embedding(embedding_text)

                # Prepare payload (all row data)
                payload = {}
                for key, value in row.items():
                    if value:  # Only include non-empty values
                        # Convert empty strings to None
                        if value == '':
                            payload[key] = None
                        # Parse boolean fields
                        elif value.lower() in ['true', 'false']:
                            payload[key] = value.lower() == 'true'
                        # Parse integer fields
                        elif key in ['id', 'user_id', 'case_id', 'patient_age',
                                   'confidence_score', 'review_tier', 'similarity_score',
                                   'probability', 'rank', 'metric_value', 'duration_ms',
                                   'failed_login_attempts', 'rate_limit', 'total_requests',
                                   'prevalence']:
                            try:
                                payload[key] = int(value)
                            except ValueError:
                                payload[key] = value
                        else:
                            payload[key] = value
                    else:
                        payload[key] = None

                # Create point
                point_id = int(row[id_field])
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                points.append(point)

                # Batch upload every 100 points
                if len(points) >= 100:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=points,
                    )
                    print(f"  Uploaded {len(points)} points to {collection_name}")
                    points = []

            # Upload remaining points
            if points:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                )
                print(f"  Uploaded {len(points)} points to {collection_name}")

        # Get collection info
        collection_info = self.client.get_collection(collection_name)
        print(f"✓ {collection_name}: {collection_info.points_count} total points")

    def search_similar(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 10,
        filters: Optional[Filter] = None,
    ) -> List[Dict]:
        """Search for similar items in a collection."""
        query_vector = self.generate_embedding(query_text)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filters,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]

    def get_by_id(self, collection_name: str, point_id: int) -> Optional[Dict]:
        """Retrieve a single point by ID."""
        points = self.client.retrieve(
            collection_name=collection_name,
            ids=[point_id],
        )

        if points:
            return {
                "id": points[0].id,
                "payload": points[0].payload,
            }
        return None

    def update_payload(
        self, collection_name: str, point_id: int, payload: Dict[str, Any]
    ):
        """Update payload for a specific point."""
        self.client.set_payload(
            collection_name=collection_name,
            payload=payload,
            points=[point_id],
        )

    def delete_point(self, collection_name: str, point_id: int):
        """Delete a point from collection."""
        self.client.delete(
            collection_name=collection_name,
            points_selector=[point_id],
        )

    def count_points(self, collection_name: str, filters: Optional[Filter] = None) -> int:
        """Count points in collection with optional filters."""
        result = self.client.count(
            collection_name=collection_name,
            count_filter=filters,
        )
        return result.count


def load_all_data():
    """Load all CSV data into Qdrant collections."""
    from src.config import settings

    # Initialize Qdrant manager
    manager = QdrantManager(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        api_key=settings.qdrant_api_key,
        vector_size=settings.embedding_dimension,
    )

    # Initialize collections
    print("=" * 60)
    print("Initializing Qdrant Collections")
    print("=" * 60)
    manager.initialize_all_collections(recreate=True)

    # Data directory
    data_dir = Path(__file__).parent.parent.parent / "data"

    # Load data for each collection
    print("\n" + "=" * 60)
    print("Loading Data from CSV Files")
    print("=" * 60)

    # Users
    manager.load_csv_to_collection(
        collection_name="users",
        csv_path=str(data_dir / "users.csv"),
        embedding_fields=["username", "full_name", "role"],
    )

    # User Sessions
    manager.load_csv_to_collection(
        collection_name="user_sessions",
        csv_path=str(data_dir / "user_sessions.csv"),
        embedding_fields=["user_agent", "device_info"],
    )

    # Audit Logs
    manager.load_csv_to_collection(
        collection_name="audit_logs",
        csv_path=str(data_dir / "audit_logs.csv"),
        embedding_fields=["action", "description"],
    )

    # API Keys
    manager.load_csv_to_collection(
        collection_name="api_keys",
        csv_path=str(data_dir / "api_keys.csv"),
        embedding_fields=["name", "description"],
    )

    # Patient Cases
    manager.load_csv_to_collection(
        collection_name="patient_cases",
        csv_path=str(data_dir / "patient_cases.csv"),
        embedding_fields=["chief_complaint", "symptoms_json"],
    )

    # Diagnosis Records
    manager.load_csv_to_collection(
        collection_name="diagnosis_records",
        csv_path=str(data_dir / "diagnosis_records.csv"),
        embedding_fields=["condition_name", "matching_symptoms_json"],
    )

    # System Metrics
    manager.load_csv_to_collection(
        collection_name="system_metrics",
        csv_path=str(data_dir / "system_metrics.csv"),
        embedding_fields=["metric_type", "metric_name"],
    )

    # Medical Conditions (Most Important!)
    manager.load_csv_to_collection(
        collection_name="medical_conditions",
        csv_path=str(data_dir / "medical_conditions.csv"),
        embedding_fields=["condition_name", "typical_symptoms_json", "rare_symptoms_json"],
    )

    print("\n" + "=" * 60)
    print("✓ Data Loading Complete!")
    print("=" * 60)


if __name__ == "__main__":
    load_all_data()
