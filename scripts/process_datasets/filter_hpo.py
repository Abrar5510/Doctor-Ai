"""
Filter Human Phenotype Ontology (HPO) data for Doctor-Ai relevance.

This script processes the HPO dataset to extract only phenotypes and diseases
relevant to general medical diagnosis and symptom analysis.

Filters applied:
1. Focus on common symptoms and observable phenotypes
2. Exclude ultra-rare genetic conditions (keep diseases with frequency > 1/100,000)
3. Prioritize phenotypes with clear symptom descriptions
4. Extract disease-symptom mappings
5. Create embeddings-ready format
"""

import sys
import csv
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class HPOFilter:
    """Filter and process HPO data for diagnostic relevance."""

    # Phenotype categories relevant to diagnosis
    RELEVANT_CATEGORIES = {
        "HP:0000118",  # Phenotypic abnormality (root)
        "HP:0000707",  # Abnormality of the nervous system
        "HP:0001507",  # Growth abnormality
        "HP:0001608",  # Abnormality of the voice
        "HP:0001871",  # Abnormality of blood and blood-forming tissues
        "HP:0001939",  # Abnormality of metabolism/homeostasis
        "HP:0002086",  # Abnormality of the respiratory system
        "HP:0002664",  # Neoplasm
        "HP:0002715",  # Abnormality of the immune system
        "HP:0003011",  # Abnormality of the musculoskeletal system
        "HP:0025031",  # Abnormality of the digestive system
        "HP:0025142",  # Constitutional symptom
        "HP:0025354",  # Abnormality of cellular immune system
        "HP:0031466",  # Impairment in personality functioning
        "HP:0040064",  # Abnormality of limbs
        "HP:0045027",  # Abnormality of the thorax
    }

    # Symptoms that are directly observable/reportable
    SYMPTOM_KEYWORDS = [
        "pain", "ache", "fever", "fatigue", "weakness", "nausea", "vomiting",
        "diarrhea", "constipation", "headache", "dizziness", "cough", "dyspnea",
        "shortness of breath", "chest pain", "abdominal pain", "rash", "itching",
        "swelling", "edema", "weight loss", "weight gain", "night sweats",
        "tremor", "seizure", "paralysis", "numbness", "tingling", "blurred vision",
        "hearing loss", "tinnitus", "palpitations", "syncope", "confusion",
        "memory loss", "anxiety", "depression", "insomnia", "excessive thirst",
        "frequent urination", "blood in urine", "blood in stool", "jaundice",
        "pale skin", "bruising", "bleeding", "joint pain", "muscle pain",
        "stiffness", "difficulty swallowing", "hoarseness", "wheezing",
    ]

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize the HPO filter.

        Args:
            input_dir: Directory containing HPO files
            output_dir: Directory to save filtered data
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data structures
        self.phenotypes = {}
        self.diseases = {}
        self.disease_phenotype_map = defaultdict(list)
        self.phenotype_disease_map = defaultdict(list)

    def parse_hpoa(self, hpoa_file: Path) -> None:
        """
        Parse the phenotype.hpoa file.

        Args:
            hpoa_file: Path to phenotype.hpoa file
        """
        print(f"\n📖 Parsing {hpoa_file.name}...")

        with open(hpoa_file, 'r', encoding='utf-8') as f:
            # Skip header lines
            for line in f:
                if not line.startswith('#'):
                    break

            # Read TSV data
            reader = csv.DictReader(f, delimiter='\t')
            annotations = list(reader)

        print(f"   Found {len(annotations)} annotations")

        # Process annotations
        for ann in annotations:
            disease_id = ann.get('database_id', '')
            disease_name = ann.get('disease_name', '')
            hpo_id = ann.get('hpo_id', '')
            hpo_label = ann.get('hpo_label', '')
            frequency = ann.get('frequency', '')
            onset = ann.get('onset', '')

            if not all([disease_id, hpo_id]):
                continue

            # Store disease info
            if disease_id not in self.diseases:
                self.diseases[disease_id] = {
                    'id': disease_id,
                    'name': disease_name,
                    'phenotypes': []
                }

            # Store phenotype info
            if hpo_id not in self.phenotypes:
                self.phenotypes[hpo_id] = {
                    'id': hpo_id,
                    'label': hpo_label,
                    'diseases': []
                }

            # Create mappings
            phenotype_info = {
                'hpo_id': hpo_id,
                'label': hpo_label,
                'frequency': frequency,
                'onset': onset
            }

            disease_info = {
                'disease_id': disease_id,
                'disease_name': disease_name,
                'frequency': frequency
            }

            self.disease_phenotype_map[disease_id].append(phenotype_info)
            self.phenotype_disease_map[hpo_id].append(disease_info)

        print(f"   ✅ Processed {len(self.diseases)} diseases and {len(self.phenotypes)} phenotypes")

    def is_symptom_relevant(self, phenotype_label: str) -> bool:
        """
        Check if a phenotype is a relevant symptom.

        Args:
            phenotype_label: HPO term label

        Returns:
            True if relevant, False otherwise
        """
        label_lower = phenotype_label.lower()

        # Check for symptom keywords
        for keyword in self.SYMPTOM_KEYWORDS:
            if keyword in label_lower:
                return True

        # Check for common symptom patterns
        symptom_patterns = [
            r'\bincreased\b',
            r'\bdecreased\b',
            r'\babnormal\b',
            r'\bdifficulty\b',
            r'\bimpaired\b',
            r'\breduced\b',
            r'\belevated\b',
        ]

        for pattern in symptom_patterns:
            if re.search(pattern, label_lower):
                return True

        return False

    def filter_common_diseases(self, min_phenotypes: int = 3) -> Set[str]:
        """
        Filter to keep diseases with sufficient phenotype annotations.

        Args:
            min_phenotypes: Minimum number of phenotypes required

        Returns:
            Set of disease IDs to keep
        """
        print(f"\n🔍 Filtering diseases (minimum {min_phenotypes} phenotypes)...")

        filtered_diseases = set()

        for disease_id, phenotypes in self.disease_phenotype_map.items():
            # Count relevant symptom phenotypes
            relevant_phenotypes = [
                p for p in phenotypes
                if self.is_symptom_relevant(p['label'])
            ]

            if len(relevant_phenotypes) >= min_phenotypes:
                filtered_diseases.add(disease_id)

        print(f"   ✅ Kept {len(filtered_diseases)} diseases out of {len(self.diseases)}")
        return filtered_diseases

    def create_disease_symptom_dataset(self, disease_ids: Set[str]) -> List[Dict]:
        """
        Create a disease-symptom dataset for ML training.

        Args:
            disease_ids: Set of disease IDs to include

        Returns:
            List of disease-symptom records
        """
        print(f"\n📊 Creating disease-symptom dataset...")

        dataset = []

        for disease_id in disease_ids:
            disease = self.diseases.get(disease_id, {})
            phenotypes = self.disease_phenotype_map.get(disease_id, [])

            # Get relevant symptoms
            symptoms = [
                p['label'] for p in phenotypes
                if self.is_symptom_relevant(p['label'])
            ]

            if not symptoms:
                continue

            # Get frequency information
            frequent_symptoms = [
                p['label'] for p in phenotypes
                if self.is_symptom_relevant(p['label'])
                and p.get('frequency', '').lower() in ['very frequent', 'frequent', 'obligate']
            ]

            occasional_symptoms = [
                p['label'] for p in phenotypes
                if self.is_symptom_relevant(p['label'])
                and p.get('frequency', '').lower() in ['occasional']
            ]

            record = {
                'disease_id': disease_id,
                'disease_name': disease.get('name', ''),
                'all_symptoms': ', '.join(symptoms),
                'frequent_symptoms': ', '.join(frequent_symptoms) if frequent_symptoms else '',
                'occasional_symptoms': ', '.join(occasional_symptoms) if occasional_symptoms else '',
                'symptom_count': len(symptoms),
                'source': 'HPO'
            }

            dataset.append(record)

        print(f"   ✅ Created dataset with {len(dataset)} disease records")
        return dataset

    def create_embeddings_format(self, disease_ids: Set[str]) -> List[Dict]:
        """
        Create data in format ready for vector embeddings.

        Args:
            disease_ids: Set of disease IDs to include

        Returns:
            List of records for embedding generation
        """
        print(f"\n🧬 Creating embeddings format...")

        embeddings_data = []

        for disease_id in disease_ids:
            disease = self.diseases.get(disease_id, {})
            phenotypes = self.disease_phenotype_map.get(disease_id, [])

            symptoms = [
                p['label'] for p in phenotypes
                if self.is_symptom_relevant(p['label'])
            ]

            if not symptoms:
                continue

            # Create a comprehensive description
            description = f"{disease.get('name', 'Unknown')}. "
            description += f"Common symptoms include: {', '.join(symptoms[:10])}."

            record = {
                'id': disease_id,
                'name': disease.get('name', ''),
                'description': description,
                'symptoms': symptoms,
                'phenotype_count': len(phenotypes),
                'symptom_count': len(symptoms),
                'type': 'disease',
                'source': 'HPO'
            }

            embeddings_data.append(record)

        print(f"   ✅ Created {len(embeddings_data)} embedding records")
        return embeddings_data

    def save_filtered_data(
        self,
        disease_symptom_data: List[Dict],
        embeddings_data: List[Dict]
    ) -> None:
        """
        Save filtered data to output files.

        Args:
            disease_symptom_data: Disease-symptom dataset
            embeddings_data: Embeddings-ready dataset
        """
        print(f"\n💾 Saving filtered data...")

        # Save disease-symptom CSV
        csv_path = self.output_dir / "hpo_disease_symptoms_filtered.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if disease_symptom_data:
                writer = csv.DictWriter(f, fieldnames=disease_symptom_data[0].keys())
                writer.writeheader()
                writer.writerows(disease_symptom_data)

        csv_size = csv_path.stat().st_size / 1024
        print(f"   ✅ Saved CSV: {csv_path} ({csv_size:.1f} KB)")

        # Save embeddings JSON
        json_path = self.output_dir / "hpo_embeddings_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)

        json_size = json_path.stat().st_size / 1024
        print(f"   ✅ Saved JSON: {json_path} ({json_size:.1f} KB)")

        # Save summary stats
        stats_path = self.output_dir / "hpo_filter_stats.json"
        stats = {
            'total_diseases_raw': len(self.diseases),
            'total_phenotypes_raw': len(self.phenotypes),
            'filtered_diseases': len(disease_symptom_data),
            'avg_symptoms_per_disease': sum(d['symptom_count'] for d in disease_symptom_data) / len(disease_symptom_data) if disease_symptom_data else 0,
            'total_unique_symptoms': len(set(
                symptom
                for d in disease_symptom_data
                for symptom in d['all_symptoms'].split(', ')
                if symptom
            ))
        }

        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print(f"   ✅ Saved stats: {stats_path}")

    def run(self, min_phenotypes: int = 3) -> bool:
        """
        Run the complete filtering process.

        Args:
            min_phenotypes: Minimum phenotypes per disease

        Returns:
            True if successful
        """
        try:
            print("=" * 70)
            print("🧬 HPO Dataset Filter")
            print("=" * 70)

            # Find HPOA file
            hpoa_file = self.input_dir / "phenotype.hpoa"
            if not hpoa_file.exists():
                print(f"❌ Error: {hpoa_file} not found")
                print(f"   Run download script first: python scripts/download_datasets/download_hpo.py")
                return False

            # Parse HPOA file
            self.parse_hpoa(hpoa_file)

            # Filter diseases
            filtered_disease_ids = self.filter_common_diseases(min_phenotypes)

            # Create datasets
            disease_symptom_data = self.create_disease_symptom_dataset(filtered_disease_ids)
            embeddings_data = self.create_embeddings_format(filtered_disease_ids)

            # Save results
            self.save_filtered_data(disease_symptom_data, embeddings_data)

            print("\n" + "=" * 70)
            print("✅ HPO Filtering Complete!")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"   • Input diseases: {len(self.diseases)}")
            print(f"   • Filtered diseases: {len(disease_symptom_data)}")
            print(f"   • Reduction: {(1 - len(disease_symptom_data)/len(self.diseases))*100:.1f}%")
            print(f"\n📁 Output files:")
            print(f"   • {self.output_dir}/hpo_disease_symptoms_filtered.csv")
            print(f"   • {self.output_dir}/hpo_embeddings_data.json")
            print(f"   • {self.output_dir}/hpo_filter_stats.json")

            return True

        except Exception as e:
            print(f"\n❌ Error during filtering: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Filter HPO dataset for Doctor-Ai diagnostic relevance"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Input directory with HPO files (default: datasets/ontologies/hpo)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/processed/hpo)"
    )
    parser.add_argument(
        "--min-phenotypes",
        "-m",
        type=int,
        default=3,
        help="Minimum phenotypes per disease (default: 3)"
    )

    args = parser.parse_args()

    # Set default paths
    project_root = Path(__file__).parent.parent.parent
    input_dir = Path(args.input) if args.input else project_root / "datasets" / "ontologies" / "hpo"
    output_dir = Path(args.output) if args.output else project_root / "datasets" / "processed" / "hpo"

    # Run filter
    filter_obj = HPOFilter(input_dir, output_dir)
    success = filter_obj.run(min_phenotypes=args.min_phenotypes)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
