"""
Filter ICD-10-CM data for Doctor-Ai relevance.

This script processes the ICD-10-CM dataset to extract only disease codes
relevant to primary care and common medical conditions.

Filters applied:
1. Focus on common diagnoses (Chapters I-XIV primarily)
2. Exclude administrative codes (Z codes), injury codes (S/T codes)
3. Prioritize diseases with clear symptom presentations
4. Create hierarchical disease categories
5. Extract disease descriptions suitable for symptom matching
"""

import sys
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class ICD10Filter:
    """Filter and process ICD-10-CM data for diagnostic relevance."""

    # ICD-10 chapter ranges (first character) we want to prioritize
    PRIORITY_CHAPTERS = {
        'A': 'Certain infectious and parasitic diseases',
        'B': 'Certain infectious and parasitic diseases',
        'C': 'Neoplasms',
        'D': 'Diseases of the blood and blood-forming organs',
        'E': 'Endocrine, nutritional and metabolic diseases',
        'F': 'Mental, behavioral and neurodevelopmental disorders',
        'G': 'Diseases of the nervous system',
        'H': 'Diseases of the eye and ear',
        'I': 'Diseases of the circulatory system',
        'J': 'Diseases of the respiratory system',
        'K': 'Diseases of the digestive system',
        'L': 'Diseases of the skin and subcutaneous tissue',
        'M': 'Diseases of the musculoskeletal system',
        'N': 'Diseases of the genitourinary system',
    }

    # Chapters to exclude (less relevant for symptom-based diagnosis)
    EXCLUDE_CHAPTERS = {
        'O': 'Pregnancy, childbirth and the puerperium',  # Specialized
        'P': 'Certain conditions originating in the perinatal period',  # Specialized
        'Q': 'Congenital malformations',  # Usually diagnosed at birth
        'S': 'Injury, poisoning (S codes)',  # Trauma
        'T': 'Injury, poisoning (T codes)',  # Trauma
        'V': 'External causes of morbidity (transport)',  # Cause codes
        'W': 'External causes of morbidity (other)',  # Cause codes
        'X': 'External causes of morbidity (assault, etc.)',  # Cause codes
        'Y': 'External causes of morbidity',  # Cause codes
        'Z': 'Factors influencing health status',  # Administrative
    }

    # Keywords indicating symptom-relevant diseases
    SYMPTOM_KEYWORDS = [
        'pain', 'syndrome', 'disorder', 'disease', 'infection', 'inflammation',
        'deficiency', 'insufficiency', 'failure', 'dysfunction', 'abnormal',
        'chronic', 'acute', 'fever', 'anemia', 'diabetes', 'hypertension',
        'arthritis', 'gastritis', 'colitis', 'itis', 'osis', 'pathy'
    ]

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize the ICD-10 filter.

        Args:
            input_dir: Directory containing ICD-10 files
            output_dir: Directory to save filtered data
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data structures
        self.codes = []
        self.filtered_codes = []
        self.category_map = defaultdict(list)

    def parse_icd10_csv(self, csv_file: Path) -> None:
        """
        Parse the ICD-10-CM CSV file.

        Args:
            csv_file: Path to ICD-10 CSV file
        """
        print(f"\n📖 Parsing {csv_file.name}...")

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.codes = list(reader)

        print(f"   Found {len(self.codes)} ICD-10 codes")

    def parse_icd10_txt(self, txt_file: Path) -> None:
        """
        Parse ICD-10-CM text file format.

        Args:
            txt_file: Path to ICD-10 text file
        """
        print(f"\n📖 Parsing {txt_file.name}...")

        codes = []

        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse "CODE Description" format
                parts = line.split(None, 1)
                if len(parts) == 2:
                    code, description = parts
                    codes.append({
                        'code': code,
                        'description': description.strip()
                    })

        self.codes = codes
        print(f"   Found {len(self.codes)} ICD-10 codes")

    def is_relevant_code(self, code: str, description: str) -> bool:
        """
        Check if an ICD-10 code is relevant for symptom-based diagnosis.

        Args:
            code: ICD-10 code
            description: Code description

        Returns:
            True if relevant, False otherwise
        """
        if not code:
            return False

        # Get first character (chapter)
        first_char = code[0].upper()

        # Exclude certain chapters
        if first_char in self.EXCLUDE_CHAPTERS:
            return False

        # Must be in priority chapters
        if first_char not in self.PRIORITY_CHAPTERS:
            return False

        # Check description for symptom-relevant keywords
        desc_lower = description.lower()

        # Exclude certain types
        exclude_terms = [
            'sequelae', 'encounter for', 'history of', 'screening',
            'examination', 'surveillance', 'follow-up', 'aftercare',
            'counseling', 'fitting', 'adjustment of', 'status post',
            'family history', 'personal history', 'carrier of'
        ]

        for term in exclude_terms:
            if term in desc_lower:
                return False

        # Check for symptom keywords
        has_symptom_keyword = any(
            keyword in desc_lower
            for keyword in self.SYMPTOM_KEYWORDS
        )

        return has_symptom_keyword or len(code) <= 5  # Include category codes

    def filter_codes(self) -> List[Dict]:
        """
        Filter ICD-10 codes for relevance.

        Returns:
            List of filtered code dictionaries
        """
        print(f"\n🔍 Filtering ICD-10 codes...")

        filtered = []

        for code_dict in self.codes:
            code = code_dict.get('code', '')
            description = code_dict.get('description', '')

            if self.is_relevant_code(code, description):
                # Add chapter information
                first_char = code[0].upper()
                code_dict['chapter'] = first_char
                code_dict['chapter_name'] = self.PRIORITY_CHAPTERS.get(first_char, 'Unknown')
                code_dict['category'] = code[:3] if len(code) >= 3 else code

                filtered.append(code_dict)

                # Add to category map
                category = code[:3] if len(code) >= 3 else code
                self.category_map[category].append(code_dict)

        self.filtered_codes = filtered
        print(f"   ✅ Kept {len(filtered)} codes out of {len(self.codes)}")
        print(f"   📉 Reduction: {(1 - len(filtered)/len(self.codes))*100:.1f}%")

        return filtered

    def create_disease_categories(self) -> List[Dict]:
        """
        Create disease categories from filtered codes.

        Returns:
            List of category summaries
        """
        print(f"\n📊 Creating disease categories...")

        categories = []

        for category_code, codes in self.category_map.items():
            if not codes:
                continue

            # Get representative description (usually from the first/shortest code)
            representative = min(codes, key=lambda x: len(x.get('code', '')))

            category_info = {
                'category_code': category_code,
                'category_name': representative.get('description', ''),
                'chapter': representative.get('chapter', ''),
                'chapter_name': representative.get('chapter_name', ''),
                'code_count': len(codes),
                'example_codes': [c.get('code', '') for c in codes[:5]]
            }

            categories.append(category_info)

        categories.sort(key=lambda x: x['category_code'])

        print(f"   ✅ Created {len(categories)} disease categories")
        return categories

    def create_embeddings_format(self) -> List[Dict]:
        """
        Create data in format ready for vector embeddings.

        Returns:
            List of records for embedding generation
        """
        print(f"\n🧬 Creating embeddings format...")

        embeddings_data = []

        # Group codes by category for better descriptions
        for category_code, codes in self.category_map.items():
            if not codes:
                continue

            # Use the category code entry (3-character code)
            category_codes = [c for c in codes if len(c.get('code', '')) == 3]
            if category_codes:
                main_code = category_codes[0]
            else:
                main_code = codes[0]

            # Create comprehensive description
            description = main_code.get('description', '')

            # Add variations if available
            if len(codes) > 1:
                variations = [c.get('description', '') for c in codes[:5] if c != main_code]
                if variations:
                    description += f". Includes: {', '.join(variations[:3])}."

            record = {
                'id': f"ICD10:{main_code.get('code', '')}",
                'code': main_code.get('code', ''),
                'name': description,
                'description': f"{main_code.get('chapter_name', '')}. {description}",
                'chapter': main_code.get('chapter', ''),
                'chapter_name': main_code.get('chapter_name', ''),
                'category': category_code,
                'related_codes': [c.get('code', '') for c in codes],
                'type': 'disease',
                'source': 'ICD10'
            }

            embeddings_data.append(record)

        print(f"   ✅ Created {len(embeddings_data)} embedding records")
        return embeddings_data

    def save_filtered_data(
        self,
        filtered_codes: List[Dict],
        categories: List[Dict],
        embeddings_data: List[Dict]
    ) -> None:
        """
        Save filtered data to output files.

        Args:
            filtered_codes: Filtered ICD-10 codes
            categories: Disease categories
            embeddings_data: Embeddings-ready dataset
        """
        print(f"\n💾 Saving filtered data...")

        # Save filtered codes CSV
        if filtered_codes:
            csv_path = self.output_dir / "icd10_codes_filtered.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=filtered_codes[0].keys())
                writer.writeheader()
                writer.writerows(filtered_codes)

            csv_size = csv_path.stat().st_size / 1024
            print(f"   ✅ Saved codes CSV: {csv_path} ({csv_size:.1f} KB)")

        # Save categories CSV
        if categories:
            cat_path = self.output_dir / "icd10_categories.csv"
            with open(cat_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=categories[0].keys())
                writer.writeheader()
                writer.writerows(categories)

            print(f"   ✅ Saved categories CSV: {cat_path}")

        # Save embeddings JSON
        json_path = self.output_dir / "icd10_embeddings_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)

        json_size = json_path.stat().st_size / 1024
        print(f"   ✅ Saved embeddings JSON: {json_path} ({json_size:.1f} KB)")

        # Save chapter breakdown
        chapter_stats = defaultdict(int)
        for code in filtered_codes:
            chapter_stats[code.get('chapter', 'Unknown')] += 1

        stats = {
            'total_codes_raw': len(self.codes),
            'filtered_codes': len(filtered_codes),
            'reduction_percent': (1 - len(filtered_codes)/len(self.codes))*100,
            'categories': len(categories),
            'chapter_breakdown': dict(chapter_stats)
        }

        stats_path = self.output_dir / "icd10_filter_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print(f"   ✅ Saved stats: {stats_path}")

    def run(self) -> bool:
        """
        Run the complete filtering process.

        Returns:
            True if successful
        """
        try:
            print("=" * 70)
            print("🏥 ICD-10-CM Dataset Filter")
            print("=" * 70)

            # Find ICD-10 file (try CSV first, then TXT)
            csv_file = self.input_dir / "icd10cm_codes_2024.csv"
            txt_files = list(self.input_dir.glob("*codes*.txt"))

            if csv_file.exists():
                self.parse_icd10_csv(csv_file)
            elif txt_files:
                self.parse_icd10_txt(txt_files[0])
            else:
                print(f"❌ Error: No ICD-10 files found in {self.input_dir}")
                print(f"   Run download script first: python scripts/download_datasets/download_icd10.py")
                return False

            # Filter codes
            filtered_codes = self.filter_codes()

            # Create categories
            categories = self.create_disease_categories()

            # Create embeddings format
            embeddings_data = self.create_embeddings_format()

            # Save results
            self.save_filtered_data(filtered_codes, categories, embeddings_data)

            print("\n" + "=" * 70)
            print("✅ ICD-10 Filtering Complete!")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"   • Input codes: {len(self.codes)}")
            print(f"   • Filtered codes: {len(filtered_codes)}")
            print(f"   • Disease categories: {len(categories)}")
            print(f"   • Reduction: {(1 - len(filtered_codes)/len(self.codes))*100:.1f}%")
            print(f"\n📁 Output files:")
            print(f"   • {self.output_dir}/icd10_codes_filtered.csv")
            print(f"   • {self.output_dir}/icd10_categories.csv")
            print(f"   • {self.output_dir}/icd10_embeddings_data.json")
            print(f"   • {self.output_dir}/icd10_filter_stats.json")

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
        description="Filter ICD-10-CM dataset for Doctor-Ai diagnostic relevance"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Input directory with ICD-10 files (default: datasets/ontologies/icd10)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/processed/icd10)"
    )

    args = parser.parse_args()

    # Set default paths
    project_root = Path(__file__).parent.parent.parent
    input_dir = Path(args.input) if args.input else project_root / "datasets" / "ontologies" / "icd10"
    output_dir = Path(args.output) if args.output else project_root / "datasets" / "processed" / "icd10"

    # Run filter
    filter_obj = ICD10Filter(input_dir, output_dir)
    success = filter_obj.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
