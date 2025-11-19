#!/usr/bin/env python3
"""
Initialize Qdrant database and load all data from CSV files.

This script:
1. Creates all required Qdrant collections
2. Loads data from CSV files in the /data directory
3. Generates embeddings for semantic search

Usage:
    python scripts/init_qdrant.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.qdrant_manager import load_all_data

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         Doctor-AI Qdrant Database Initialization         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        load_all_data()
        print("\n✓ Qdrant database initialized successfully!")
        print("\nYou can now start the application and use Qdrant as the primary database.")
    except Exception as e:
        print(f"\n✗ Error initializing Qdrant database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
