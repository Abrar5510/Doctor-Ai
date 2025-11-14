"""
Index filtered medical datasets into Qdrant vector database.

This script reads the unified disease dataset and creates vector embeddings
using BioBERT/PubMedBERT, then indexes them in Qdrant for similarity search.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict
import asyncio

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.services.embedding import EmbeddingService
    from src.services.vector_store import VectorStore
    from src.config import settings
except ImportError as e:
    print(f"⚠️ Warning: Could not import project modules: {e}")
    print("   This script requires the Doctor-Ai services to be available.")
    EmbeddingService = None
    VectorStore = None


class QdrantIndexer:
    """Index medical datasets in Qdrant."""

    def __init__(self, input_file: Path, collection_name: str = None):
        """
        Initialize the Qdrant indexer.

        Args:
            input_file: Path to unified diseases JSON file
            collection_name: Qdrant collection name
        """
        self.input_file = input_file
        self.collection_name = collection_name or "medical_conditions"

        # Initialize services (if available)
        self.embedding_service = None
        self.vector_store = None

    async def initialize_services(self):
        """Initialize embedding and vector store services."""
        if EmbeddingService is None or VectorStore is None:
            print("❌ Services not available. Please ensure Doctor-Ai is properly installed.")
            return False

        try:
            print("\n🔧 Initializing services...")

            self.embedding_service = EmbeddingService()
            self.vector_store = VectorStore()

            print("   ✅ Services initialized")
            return True

        except Exception as e:
            print(f"   ❌ Error initializing services: {e}")
            return False

    def load_unified_data(self) -> List[Dict]:
        """
        Load the unified disease dataset.

        Returns:
            List of disease records
        """
        print(f"\n📖 Loading unified dataset from {self.input_file}...")

        if not self.input_file.exists():
            print(f"   ❌ File not found: {self.input_file}")
            print(f"   Run merge script first: python scripts/process_datasets/merge_all_datasets.py")
            return []

        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"   ✅ Loaded {len(data)} disease records")
        return data

    async def create_embeddings(self, diseases: List[Dict]) -> List[Dict]:
        """
        Create embeddings for diseases.

        Args:
            diseases: List of disease records

        Returns:
            List of diseases with embeddings
        """
        print(f"\n🧬 Creating embeddings for {len(diseases)} diseases...")

        diseases_with_embeddings = []

        for i, disease in enumerate(diseases):
            if i % 100 == 0 and i > 0:
                print(f"   Progress: {i}/{len(diseases)}")

            # Use description for embedding
            text = disease.get('description', disease.get('name', ''))

            if not text:
                continue

            try:
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(text)

                disease['embedding'] = embedding
                diseases_with_embeddings.append(disease)

            except Exception as e:
                print(f"   ⚠️ Error creating embedding for {disease.get('name', 'unknown')}: {e}")
                continue

        print(f"   ✅ Created {len(diseases_with_embeddings)} embeddings")
        return diseases_with_embeddings

    async def index_in_qdrant(self, diseases: List[Dict]) -> bool:
        """
        Index diseases in Qdrant.

        Args:
            diseases: List of diseases with embeddings

        Returns:
            True if successful
        """
        print(f"\n📥 Indexing {len(diseases)} diseases in Qdrant...")

        try:
            # Prepare points for Qdrant
            points = []

            for disease in diseases:
                if 'embedding' not in disease:
                    continue

                # Prepare payload
                payload = {
                    'id': disease.get('id', ''),
                    'name': disease.get('name', ''),
                    'description': disease.get('description', ''),
                    'symptoms': disease.get('symptoms', []),
                    'sources': disease.get('sources', [disease.get('source', '')]),
                    'type': disease.get('type', 'disease'),
                }

                # Add optional fields
                if 'icd10_codes' in disease:
                    payload['icd10_codes'] = disease['icd10_codes']

                if 'chapter' in disease:
                    payload['chapter'] = disease['chapter']
                    payload['chapter_name'] = disease.get('chapter_name', '')

                points.append({
                    'id': disease.get('id', ''),
                    'vector': disease['embedding'],
                    'payload': payload
                })

            # Batch index
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                await self.vector_store.upsert_points(
                    collection_name=self.collection_name,
                    points=batch
                )

                if i % 500 == 0 and i > 0:
                    print(f"   Progress: {i}/{len(points)} indexed")

            print(f"   ✅ Successfully indexed {len(points)} diseases")
            return True

        except Exception as e:
            print(f"   ❌ Error indexing in Qdrant: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run(self) -> bool:
        """
        Run the complete indexing process.

        Returns:
            True if successful
        """
        try:
            print("=" * 70)
            print("📥 Qdrant Disease Indexer")
            print("=" * 70)

            # Initialize services
            if not await self.initialize_services():
                print("\n⚠️ Running in dry-run mode (services not available)")
                print("   The script will load and validate data only.\n")

            # Load unified data
            diseases = self.load_unified_data()

            if not diseases:
                return False

            # If services available, create embeddings and index
            if self.embedding_service and self.vector_store:
                # Create embeddings
                diseases_with_embeddings = await self.create_embeddings(diseases)

                if not diseases_with_embeddings:
                    print("\n❌ No embeddings created")
                    return False

                # Index in Qdrant
                success = await self.index_in_qdrant(diseases_with_embeddings)

                if success:
                    print("\n" + "=" * 70)
                    print("✅ Qdrant Indexing Complete!")
                    print("=" * 70)
                    print(f"\n📊 Summary:")
                    print(f"   • Total diseases indexed: {len(diseases_with_embeddings)}")
                    print(f"   • Collection: {self.collection_name}")
                    print(f"\n🔍 Next steps:")
                    print(f"   • Test the API: python scripts/test_api.py")
                    print(f"   • Query diseases: Use the /api/v1/analyze endpoint")

                return success
            else:
                print("\n✅ Data validation complete!")
                print(f"   {len(diseases)} diseases ready for indexing")
                print("\n   To index in Qdrant, ensure:")
                print("   1. Qdrant is running (docker-compose up -d)")
                print("   2. Doctor-Ai services are available")
                return True

        except Exception as e:
            print(f"\n❌ Error during indexing: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Index filtered medical datasets in Qdrant vector database"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Input unified diseases JSON file (default: datasets/processed/unified/unified_diseases.json)"
    )
    parser.add_argument(
        "--collection",
        "-c",
        type=str,
        default="medical_conditions",
        help="Qdrant collection name (default: medical_conditions)"
    )

    args = parser.parse_args()

    # Set default paths
    project_root = Path(__file__).parent.parent.parent
    input_file = Path(args.input) if args.input else project_root / "datasets" / "processed" / "unified" / "unified_diseases.json"

    # Run indexer
    indexer = QdrantIndexer(input_file, args.collection)

    # Run async
    success = asyncio.run(indexer.run())

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
