"""
Vector embedding service using BioBERT/PubMedBERT for medical text
"""

from typing import List, Union, Optional
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from loguru import logger
from functools import lru_cache

from ..config import get_settings


class EmbeddingService:
    """
    Service for generating vector embeddings from medical text using
    biomedical language models (BioBERT, PubMedBERT, etc.)
    """

    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()

    def _get_device(self) -> str:
        """Determine the best device for model inference"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def initialize(self):
        """Initialize the embedding model and tokenizer"""
        if self.model is not None:
            return  # Already initialized

        try:
            logger.info(f"Loading embedding model: {self.settings.embedding_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.embedding_model)
            self.model = AutoModel.from_pretrained(self.settings.embedding_model)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            logger.info(f"Model loaded successfully on device: {self.device}")

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def _mean_pooling(self, model_output, attention_mask) -> torch.Tensor:
        """
        Perform mean pooling on model output to get sentence embeddings

        Args:
            model_output: Output from the transformer model
            attention_mask: Attention mask for valid tokens

        Returns:
            Mean-pooled embeddings
        """
        token_embeddings = model_output[0]  # First element contains token embeddings
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate embeddings for medical text

        Args:
            texts: Single text or list of texts to embed
            normalize: Whether to normalize embeddings (for cosine similarity)
            batch_size: Batch size for processing multiple texts

        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self.initialize()

        # Handle single text input
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenize
            encoded_input = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.settings.max_sequence_length,
                return_tensors='pt'
            )

            # Move to device
            encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

            # Generate embeddings
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                embeddings = self._mean_pooling(
                    model_output,
                    encoded_input['attention_mask']
                )

            # Normalize if requested
            if normalize:
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            all_embeddings.append(embeddings.cpu().numpy())

        # Concatenate all batches
        result = np.vstack(all_embeddings)

        logger.debug(f"Generated {len(result)} embeddings of dimension {result.shape[1]}")

        return result

    def encode_symptom_constellation(
        self,
        symptoms: List[str],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Generate a weighted embedding for a constellation of symptoms

        Args:
            symptoms: List of symptom descriptions
            weights: Optional weights for each symptom (e.g., based on severity or rarity)

        Returns:
            Single embedding vector representing the symptom constellation
        """
        if not symptoms:
            raise ValueError("At least one symptom is required")

        # Generate embeddings for all symptoms
        symptom_embeddings = self.encode(symptoms, normalize=True)

        # Apply weights if provided
        if weights is not None:
            if len(weights) != len(symptoms):
                raise ValueError("Number of weights must match number of symptoms")
            weights_array = np.array(weights).reshape(-1, 1)
            symptom_embeddings = symptom_embeddings * weights_array

        # Compute weighted average
        constellation_embedding = np.mean(symptom_embeddings, axis=0, keepdims=True)

        # Normalize the final embedding
        constellation_embedding = constellation_embedding / np.linalg.norm(
            constellation_embedding
        )

        return constellation_embedding

    def encode_medical_condition(
        self,
        condition_name: str,
        typical_symptoms: List[str],
        rare_symptoms: Optional[List[str]] = None,
        temporal_pattern: Optional[str] = None
    ) -> np.ndarray:
        """
        Generate a comprehensive embedding for a medical condition

        Args:
            condition_name: Name of the medical condition
            typical_symptoms: List of typical symptoms
            rare_symptoms: List of rare but diagnostic symptoms
            temporal_pattern: Description of temporal progression

        Returns:
            Embedding vector for the condition
        """
        # Build comprehensive description
        description_parts = [condition_name]

        if typical_symptoms:
            description_parts.append("Typical symptoms: " + ", ".join(typical_symptoms))

        if rare_symptoms:
            description_parts.append("Rare symptoms: " + ", ".join(rare_symptoms))

        if temporal_pattern:
            description_parts.append("Temporal pattern: " + temporal_pattern)

        full_description = ". ".join(description_parts)

        # Generate embedding
        embedding = self.encode(full_description, normalize=True)

        return embedding

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        # Ensure embeddings are normalized
        emb1_norm = embedding1 / np.linalg.norm(embedding1)
        emb2_norm = embedding2 / np.linalg.norm(embedding2)

        # Compute dot product (cosine similarity for normalized vectors)
        similarity = np.dot(emb1_norm.flatten(), emb2_norm.flatten())

        return float(similarity)

    @lru_cache(maxsize=1000)
    def encode_cached(self, text: str) -> np.ndarray:
        """
        Cached version of encode for frequently used texts

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self.encode(text, normalize=True)

    def shutdown(self):
        """Clean up resources"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("Embedding service shut down")
