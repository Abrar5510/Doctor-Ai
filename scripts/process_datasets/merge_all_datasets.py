"""
Merge and deduplicate all filtered medical datasets for Doctor-Ai.

This script combines data from:
1. Filtered HPO dataset (rare diseases + phenotypes)
2. Filtered ICD-10 dataset (common diseases)
3. Sample disease-symptom datasets

Creates a unified, deduplicated dataset ready for Qdrant indexing.
"""

import sys
import csv
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class DatasetMerger:
    """Merge and deduplicate medical datasets."""

    def __init__(self, processed_dir: Path, output_dir: Path):
        """
        Initialize the dataset merger.

        Args:
            processed_dir: Directory containing processed datasets
            output_dir: Directory to save merged data
        """
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data structures
        self.diseases = {}  # disease_id -> disease info
        self.disease_names_map = {}  # lowercase name -> canonical disease
        self.merged_embeddings = []

    def load_hpo_data(self) -> None:
        """Load filtered HPO data."""
        print(f"\n📖 Loading HPO data...")

        hpo_dir = self.processed_dir / "hpo"
        embeddings_file = hpo_dir / "hpo_embeddings_data.json"

        if not embeddings_file.exists():
            print(f"   ⚠️ HPO embeddings file not found: {embeddings_file}")
            print(f"   Run: python scripts/process_datasets/filter_hpo.py")
            return

        with open(embeddings_file, 'r', encoding='utf-8') as f:
            hpo_data = json.load(f)

        print(f"   Found {len(hpo_data)} HPO diseases")

        for disease in hpo_data:
            disease_id = disease.get('id', '')
            disease_name = disease.get('name', '').lower()

            # Store disease
            self.diseases[disease_id] = disease

            # Map name to ID for deduplication
            if disease_name:
                self.disease_names_map[disease_name] = disease_id

        print(f"   ✅ Loaded {len(hpo_data)} HPO diseases")

    def load_icd10_data(self) -> None:
        """Load filtered ICD-10 data."""
        print(f"\n📖 Loading ICD-10 data...")

        icd10_dir = self.processed_dir / "icd10"
        embeddings_file = icd10_dir / "icd10_embeddings_data.json"

        if not embeddings_file.exists():
            print(f"   ⚠️ ICD-10 embeddings file not found: {embeddings_file}")
            print(f"   Run: python scripts/process_datasets/filter_icd10.py")
            return

        with open(embeddings_file, 'r', encoding='utf-8') as f:
            icd10_data = json.load(f)

        print(f"   Found {len(icd10_data)} ICD-10 diseases")

        added = 0
        merged = 0

        for disease in icd10_data:
            disease_id = disease.get('id', '')
            disease_name = disease.get('name', '').lower()

            # Check if disease already exists (by name)
            if disease_name in self.disease_names_map:
                # Merge with existing disease
                existing_id = self.disease_names_map[disease_name]
                existing = self.diseases[existing_id]

                # Add ICD-10 code to existing disease
                if 'icd10_codes' not in existing:
                    existing['icd10_codes'] = []
                existing['icd10_codes'].append(disease.get('code', ''))

                # Add to sources
                if 'sources' not in existing:
                    existing['sources'] = [existing.get('source', '')]
                if 'ICD10' not in existing['sources']:
                    existing['sources'].append('ICD10')

                merged += 1
            else:
                # Add as new disease
                self.diseases[disease_id] = disease
                self.disease_names_map[disease_name] = disease_id
                added += 1

        print(f"   ✅ Added {added} new diseases, merged {merged} with existing")

    def load_sample_data(self) -> None:
        """Load sample disease-symptom data."""
        print(f"\n📖 Loading sample disease-symptom data...")

        samples_dir = self.processed_dir.parent / "samples"
        sample_file = samples_dir / "disease_symptom_sample.csv"

        if not sample_file.exists():
            print(f"   ℹ️ No sample data found at {sample_file}")
            return

        with open(sample_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sample_data = list(reader)

        print(f"   Found {len(sample_data)} sample diseases")

        added = 0
        merged = 0

        for row in sample_data:
            disease_name = row.get('disease', '').lower()
            symptoms = row.get('symptoms', '')

            if not disease_name:
                continue

            # Check if disease exists
            if disease_name in self.disease_names_map:
                # Merge symptoms with existing
                existing_id = self.disease_names_map[disease_name]
                existing = self.diseases[existing_id]

                # Add symptoms if not already present
                existing_symptoms = existing.get('symptoms', [])
                new_symptoms = [s.strip() for s in symptoms.split(',')]

                for symptom in new_symptoms:
                    if symptom and symptom not in existing_symptoms:
                        existing_symptoms.append(symptom)

                existing['symptoms'] = existing_symptoms

                # Update description
                if existing_symptoms:
                    existing['description'] = f"{existing.get('name', '')}. Common symptoms include: {', '.join(existing_symptoms[:10])}."

                merged += 1
            else:
                # Add as new disease
                disease_id = f"SAMPLE:{disease_name.replace(' ', '_').upper()}"
                new_symptoms = [s.strip() for s in symptoms.split(',')]

                disease = {
                    'id': disease_id,
                    'name': row.get('disease', ''),
                    'description': f"{row.get('disease', '')}. Common symptoms include: {symptoms}.",
                    'symptoms': new_symptoms,
                    'severity': row.get('severity', ''),
                    'frequency': row.get('frequency', ''),
                    'type': 'disease',
                    'source': 'SAMPLE'
                }

                self.diseases[disease_id] = disease
                self.disease_names_map[disease_name] = disease_id
                added += 1

        print(f"   ✅ Added {added} new diseases, merged {merged} with existing")

    def create_unified_dataset(self) -> List[Dict]:
        """
        Create unified embeddings dataset.

        Returns:
            List of disease records for embeddings
        """
        print(f"\n🔗 Creating unified dataset...")

        unified = []

        for disease_id, disease in self.diseases.items():
            # Ensure required fields
            if 'description' not in disease or not disease['description']:
                symptoms = disease.get('symptoms', [])
                if symptoms:
                    disease['description'] = f"{disease.get('name', '')}. Common symptoms include: {', '.join(symptoms[:10])}."
                else:
                    disease['description'] = disease.get('name', '')

            # Ensure type field
            if 'type' not in disease:
                disease['type'] = 'disease'

            # Normalize sources
            sources = disease.get('sources', [disease.get('source', '')])
            disease['sources'] = [s for s in sources if s]

            unified.append(disease)

        # Sort by source priority (HPO > ICD10 > SAMPLE)
        source_priority = {'HPO': 1, 'ICD10': 2, 'SAMPLE': 3}

        def get_priority(disease):
            sources = disease.get('sources', [disease.get('source', '')])
            priorities = [source_priority.get(s, 99) for s in sources]
            return min(priorities) if priorities else 99

        unified.sort(key=get_priority)

        print(f"   ✅ Created unified dataset with {len(unified)} diseases")
        return unified

    def save_merged_data(self, unified_data: List[Dict]) -> None:
        """
        Save merged dataset.

        Args:
            unified_data: Unified disease dataset
        """
        print(f"\n💾 Saving merged data...")

        # Save JSON for embeddings
        json_path = self.output_dir / "unified_diseases.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=2, ensure_ascii=False)

        json_size = json_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Saved JSON: {json_path} ({json_size:.2f} MB)")

        # Save CSV for easy viewing
        if unified_data:
            csv_path = self.output_dir / "unified_diseases.csv"

            # Flatten for CSV
            csv_data = []
            for disease in unified_data:
                row = {
                    'id': disease.get('id', ''),
                    'name': disease.get('name', ''),
                    'description': disease.get('description', ''),
                    'source': ', '.join(disease.get('sources', [disease.get('source', '')])),
                    'symptom_count': len(disease.get('symptoms', [])),
                    'symptoms_preview': ', '.join(disease.get('symptoms', [])[:5])
                }
                csv_data.append(row)

            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)

            print(f"   ✅ Saved CSV: {csv_path}")

        # Save statistics
        source_counts = defaultdict(int)
        symptom_counts = []

        for disease in unified_data:
            sources = disease.get('sources', [disease.get('source', '')])
            for source in sources:
                if source:
                    source_counts[source] += 1

            symptom_count = len(disease.get('symptoms', []))
            if symptom_count > 0:
                symptom_counts.append(symptom_count)

        stats = {
            'total_diseases': len(unified_data),
            'source_breakdown': dict(source_counts),
            'avg_symptoms_per_disease': sum(symptom_counts) / len(symptom_counts) if symptom_counts else 0,
            'diseases_with_symptoms': len(symptom_counts),
            'unique_disease_names': len(self.disease_names_map)
        }

        stats_path = self.output_dir / "merge_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print(f"   ✅ Saved stats: {stats_path}")

    def run(self) -> bool:
        """
        Run the complete merging process.

        Returns:
            True if successful
        """
        try:
            print("=" * 70)
            print("🔗 Medical Dataset Merger")
            print("=" * 70)

            # Load all datasets
            self.load_hpo_data()
            self.load_icd10_data()
            self.load_sample_data()

            if not self.diseases:
                print("\n❌ No datasets loaded. Please run filter scripts first:")
                print("   python scripts/process_datasets/filter_hpo.py")
                print("   python scripts/process_datasets/filter_icd10.py")
                return False

            # Create unified dataset
            unified_data = self.create_unified_dataset()

            # Save merged data
            self.save_merged_data(unified_data)

            print("\n" + "=" * 70)
            print("✅ Dataset Merging Complete!")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"   • Total diseases: {len(unified_data)}")
            print(f"   • Unique disease names: {len(self.disease_names_map)}")
            print(f"\n📁 Output files:")
            print(f"   • {self.output_dir}/unified_diseases.json")
            print(f"   • {self.output_dir}/unified_diseases.csv")
            print(f"   • {self.output_dir}/merge_stats.json")
            print(f"\n🔍 Next step:")
            print(f"   Index in Qdrant: python scripts/process_datasets/index_in_qdrant.py")

            return True

        except Exception as e:
            print(f"\n❌ Error during merging: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge filtered medical datasets into unified format"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Input directory with processed datasets (default: datasets/processed)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/processed/unified)"
    )

    args = parser.parse_args()

    # Set default paths
    project_root = Path(__file__).parent.parent.parent
    input_dir = Path(args.input) if args.input else project_root / "datasets" / "processed"
    output_dir = Path(args.output) if args.output else project_root / "datasets" / "processed" / "unified"

    # Run merger
    merger = DatasetMerger(input_dir, output_dir)
    success = merger.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
