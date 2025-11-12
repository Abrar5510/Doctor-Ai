#!/usr/bin/env python3
"""
Test script to verify Qdrant connection and setup
"""

import sys
from typing import Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
except ImportError:
    print("❌ Error: qdrant-client not installed")
    print("   Run: pip install qdrant-client==1.7.0")
    sys.exit(1)

def test_connection(host: str = "localhost", port: int = 6333, api_key: Optional[str] = None) -> bool:
    """Test connection to Qdrant"""
    print(f"Testing connection to Qdrant at {host}:{port}...")

    try:
        client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=5
        )

        # Try to get collections
        collections = client.get_collections()

        print(f"✅ Successfully connected to Qdrant!")
        print(f"   Host: {host}:{port}")
        print(f"   Collections found: {len(collections.collections)}")

        if collections.collections:
            print("\n   Existing collections:")
            for col in collections.collections:
                print(f"     - {col.name}")

        return True

    except Exception as e:
        print(f"❌ Failed to connect to Qdrant")
        print(f"   Error: {str(e)}")
        print(f"\n   Troubleshooting:")
        print(f"   1. Make sure Qdrant is running")
        print(f"   2. Check if the host and port are correct")
        print(f"   3. If using Docker: docker-compose up -d qdrant")
        print(f"   4. See QDRANT_SETUP.md for more options")
        return False

def test_create_collection(host: str = "localhost", port: int = 6333, api_key: Optional[str] = None) -> bool:
    """Test creating a test collection"""
    print("\nTesting collection creation...")

    try:
        client = QdrantClient(host=host, port=port, api_key=api_key, timeout=5)

        test_collection = "test_collection"

        # Check if test collection exists
        collections = client.get_collections()
        exists = any(col.name == test_collection for col in collections.collections)

        if exists:
            print(f"   Deleting existing test collection...")
            client.delete_collection(test_collection)

        # Create test collection
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE)
        )

        print(f"✅ Successfully created test collection!")

        # Clean up
        client.delete_collection(test_collection)
        print(f"   Test collection cleaned up")

        return True

    except Exception as e:
        print(f"❌ Failed to create collection")
        print(f"   Error: {str(e)}")
        return False

def test_medical_conditions_collection(
    host: str = "localhost",
    port: int = 6333,
    api_key: Optional[str] = None,
    collection_name: str = "medical_conditions"
) -> bool:
    """Check if the medical_conditions collection exists"""
    print(f"\nChecking for '{collection_name}' collection...")

    try:
        client = QdrantClient(host=host, port=port, api_key=api_key, timeout=5)
        collections = client.get_collections()

        exists = any(col.name == collection_name for col in collections.collections)

        if exists:
            print(f"✅ '{collection_name}' collection exists!")

            # Get collection info
            collection_info = client.get_collection(collection_name)
            print(f"   Points count: {collection_info.points_count}")
            print(f"   Vector size: {collection_info.config.params.vectors.size}")
            print(f"   Distance: {collection_info.config.params.vectors.distance}")

        else:
            print(f"⚠️  '{collection_name}' collection not found")
            print(f"   Run: python scripts/seed_data.py")

        return exists

    except Exception as e:
        print(f"❌ Error checking collection")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("  Qdrant Connection Test")
    print("=" * 60)
    print()

    # Read from environment or use defaults
    import os
    from pathlib import Path

    # Try to load .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Loaded configuration from .env file")
        except ImportError:
            print("⚠️  python-dotenv not installed, using default values")
    else:
        print("⚠️  .env file not found, using default values")

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    api_key = os.getenv("QDRANT_API_KEY", None)
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "medical_conditions")

    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   API Key: {'Set' if api_key else 'Not set'}")
    print()

    # Run tests
    tests_passed = 0
    tests_total = 3

    if test_connection(host, port, api_key):
        tests_passed += 1

    if test_create_collection(host, port, api_key):
        tests_passed += 1

    if test_medical_conditions_collection(host, port, api_key, collection_name):
        tests_passed += 1

    # Summary
    print()
    print("=" * 60)
    print(f"  Test Results: {tests_passed}/{tests_total} passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print()
        print("🎉 All tests passed! Qdrant is ready to use.")
        print()
        print("Next steps:")
        print("  1. If medical_conditions collection is empty:")
        print("     python scripts/seed_data.py")
        print("  2. Start the API:")
        print("     python -m uvicorn src.main:app --reload")
        sys.exit(0)
    else:
        print()
        print("⚠️  Some tests failed. Please check QDRANT_SETUP.md for help.")
        sys.exit(1)

if __name__ == "__main__":
    main()
