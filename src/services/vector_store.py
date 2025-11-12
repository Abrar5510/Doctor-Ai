"""
Qdrant vector database service for similarity search
"""

from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    SearchParams,
)
from loguru import logger
import numpy as np
from uuid import uuid4

from ..config import get_settings
from ..models.schemas import MedicalCondition, UrgencyLevel


class VectorStoreService:
    """
    Service for managing medical condition vectors in Qdrant
    """

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[QdrantClient] = None
        self.collection_name = self.settings.qdrant_collection_name

    def initialize(self):
        """Initialize connection to Qdrant"""
        if self.client is not None:
            return  # Already initialized

        try:
            logger.info(f"Connecting to Qdrant at {self.settings.qdrant_host}:{self.settings.qdrant_port}")

            self.client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                api_key=self.settings.qdrant_api_key,
            )

            # Check connection
            collections = self.client.get_collections()
            logger.info(f"Connected to Qdrant. Found {len(collections.collections)} collections")

        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def create_collection(self, recreate: bool = False):
        """
        Create the medical conditions collection in Qdrant

        Args:
            recreate: If True, delete existing collection and recreate
        """
        if self.client is None:
            self.initialize()

        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(
                col.name == self.collection_name
                for col in collections.collections
            )

            if collection_exists:
                if recreate:
                    logger.warning(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return

            # Create collection
            logger.info(f"Creating collection: {self.collection_name}")

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload indexes for efficient filtering
            self._create_indexes()

            logger.info(f"Collection {self.collection_name} created successfully")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def _create_indexes(self):
        """Create payload indexes for efficient filtering"""
        try:
            # Index for condition name (full-text search)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="condition_name",
                field_schema="keyword",
            )

            # Index for ICD codes
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="icd_codes",
                field_schema="keyword",
            )

            # Index for prevalence (range queries)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="prevalence",
                field_schema="float",
            )

            # Index for rare disease status
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="is_rare_disease",
                field_schema="bool",
            )

            # Index for urgency level
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="urgency_level",
                field_schema="keyword",
            )

            logger.info("Payload indexes created successfully")

        except Exception as e:
            logger.warning(f"Some indexes may already exist: {e}")

    def add_condition(
        self,
        condition: MedicalCondition,
        embedding: np.ndarray
    ) -> str:
        """
        Add a medical condition to the vector database

        Args:
            condition: Medical condition data
            embedding: Vector embedding for the condition

        Returns:
            Point ID of the inserted condition
        """
        if self.client is None:
            self.initialize()

        try:
            point_id = condition.condition_id

            # Prepare payload (all metadata)
            payload = condition.model_dump(exclude={"embedding_metadata"})

            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding.flatten().tolist(),
                payload=payload,
            )

            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.debug(f"Added condition: {condition.condition_name} (ID: {point_id})")

            return point_id

        except Exception as e:
            logger.error(f"Failed to add condition: {e}")
            raise

    def add_conditions_batch(
        self,
        conditions: List[MedicalCondition],
        embeddings: np.ndarray
    ) -> List[str]:
        """
        Add multiple medical conditions in batch

        Args:
            conditions: List of medical conditions
            embeddings: Array of embeddings (one per condition)

        Returns:
            List of point IDs
        """
        if self.client is None:
            self.initialize()

        if len(conditions) != len(embeddings):
            raise ValueError("Number of conditions must match number of embeddings")

        try:
            points = []
            point_ids = []

            for condition, embedding in zip(conditions, embeddings):
                point_id = condition.condition_id
                point_ids.append(point_id)

                payload = condition.model_dump(exclude={"embedding_metadata"})

                point = PointStruct(
                    id=point_id,
                    vector=embedding.flatten().tolist(),
                    payload=payload,
                )
                points.append(point)

            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(f"Added {len(conditions)} conditions to vector database")

            return point_ids

        except Exception as e:
            logger.error(f"Failed to add conditions batch: {e}")
            raise

    def search(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[MedicalCondition, float]]:
        """
        Search for similar medical conditions

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            filters: Optional filters (e.g., age, sex, prevalence)

        Returns:
            List of (MedicalCondition, similarity_score) tuples
        """
        if self.client is None:
            self.initialize()

        try:
            # Build filter if provided
            query_filter = None
            if filters:
                query_filter = self._build_filter(filters)

            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.flatten().tolist(),
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )

            # Convert results to MedicalCondition objects
            results = []
            for scored_point in search_result:
                condition = MedicalCondition(**scored_point.payload)
                similarity_score = scored_point.score
                results.append((condition, similarity_score))

            logger.debug(f"Found {len(results)} matching conditions")

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def search_rare_diseases(
        self,
        query_vector: np.ndarray,
        limit: int = 20,
        score_threshold: float = 0.6
    ) -> List[Tuple[MedicalCondition, float]]:
        """
        Specialized search for rare diseases

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of rare disease matches
        """
        filters = {"is_rare_disease": True}

        return self.search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters
        )

    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from dictionary

        Args:
            filters: Dictionary of filter conditions

        Returns:
            Qdrant Filter object
        """
        must_conditions = []

        for key, value in filters.items():
            if key == "is_rare_disease" and isinstance(value, bool):
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            elif key == "urgency_level":
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            elif key == "min_prevalence":
                must_conditions.append(
                    FieldCondition(
                        key="prevalence",
                        range=Range(gte=value)
                    )
                )
            elif key == "max_prevalence":
                must_conditions.append(
                    FieldCondition(
                        key="prevalence",
                        range=Range(lte=value)
                    )
                )

        return Filter(must=must_conditions) if must_conditions else None

    def get_condition_by_id(self, condition_id: str) -> Optional[MedicalCondition]:
        """
        Retrieve a specific condition by ID

        Args:
            condition_id: Condition identifier

        Returns:
            MedicalCondition if found, None otherwise
        """
        if self.client is None:
            self.initialize()

        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[condition_id],
            )

            if points:
                return MedicalCondition(**points[0].payload)
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve condition: {e}")
            return None

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection statistics
        """
        if self.client is None:
            self.initialize()

        try:
            collection_info = self.client.get_collection(self.collection_name)

            stats = {
                "total_conditions": collection_info.points_count,
                "vector_dimension": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance,
            }

            logger.debug(f"Collection stats: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

    def shutdown(self):
        """Clean up resources"""
        if self.client is not None:
            self.client = None
            logger.info("Vector store service shut down")
