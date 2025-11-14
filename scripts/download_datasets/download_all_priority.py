"""
Master script to download all priority medical datasets for Doctor-Ai.

This script coordinates the download of:
1. Human Phenotype Ontology (HPO)
2. ICD-10-CM codes
3. Disease-Symptom datasets

All datasets are selected to be within GitHub's file size limits.
"""

import sys
from pathlib import Path
import argparse
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import download modules
try:
    from scripts.download_datasets.download_hpo import download_hpo
    from scripts.download_datasets.download_icd10 import download_icd10
    from scripts.download_datasets.download_disease_symptoms import download_disease_symptoms
except ImportError:
    print("⚠️ Could not import download modules. Running from script directory...")
    # Try importing without package prefix
    try:
        from download_hpo import download_hpo
        from download_icd10 import download_icd10
        from download_disease_symptoms import download_disease_symptoms
    except ImportError:
        print("❌ Failed to import download modules.")
        print("   Please run this script from the project root or scripts/download_datasets directory")
        sys.exit(1)


def print_header():
    """Print the script header."""
    print("=" * 70)
    print("🏥 Doctor-Ai Medical Datasets Downloader")
    print("=" * 70)
    print("\nThis script will download priority medical datasets:")
    print("  1. 🧬 Human Phenotype Ontology (HPO)")
    print("  2. 🏥 ICD-10-CM Disease Codes")
    print("  3. 🩺 Disease-Symptom Datasets")
    print("\nAll datasets are within GitHub size limits (<50MB each)")
    print("=" * 70)


def download_all_datasets(
    base_output_dir: Optional[str] = None,
    include_optional_hpo: bool = False,
    use_kaggle: bool = False,
    datasets_to_download: Optional[List[str]] = None
) -> Dict[str, bool]:
    """
    Download all priority datasets.

    Args:
        base_output_dir: Base directory for all datasets
        include_optional_hpo: Whether to download optional HPO files
        use_kaggle: Whether to use Kaggle API for disease datasets
        datasets_to_download: List of datasets to download (None = all)

    Returns:
        Dictionary mapping dataset names to success status
    """
    # Set default output directory
    if base_output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        base_output_dir = project_root / "datasets"
    else:
        base_output_dir = Path(base_output_dir)

    results = {}

    # Define all datasets
    all_datasets = {
        "hpo": {
            "name": "Human Phenotype Ontology",
            "function": lambda: download_hpo(
                output_dir=base_output_dir / "ontologies" / "hpo",
                include_optional=include_optional_hpo
            )
        },
        "icd10": {
            "name": "ICD-10-CM",
            "function": lambda: download_icd10(
                output_dir=base_output_dir / "ontologies" / "icd10",
                create_csv=True
            )
        },
        "disease_symptoms": {
            "name": "Disease-Symptom Datasets",
            "function": lambda: download_disease_symptoms(
                output_dir=base_output_dir / "samples",
                use_kaggle=use_kaggle,
                create_sample=True
            )
        }
    }

    # Filter datasets if specific ones requested
    if datasets_to_download:
        datasets = {k: v for k, v in all_datasets.items() if k in datasets_to_download}
    else:
        datasets = all_datasets

    # Download each dataset
    for dataset_key, dataset_info in datasets.items():
        print(f"\n{'=' * 70}")
        print(f"📦 Downloading: {dataset_info['name']}")
        print(f"{'=' * 70}")

        try:
            success = dataset_info["function"]()
            results[dataset_key] = success
        except Exception as e:
            print(f"\n❌ Error downloading {dataset_info['name']}: {e}")
            results[dataset_key] = False

    return results


def print_summary(results: Dict[str, bool]):
    """
    Print a summary of download results.

    Args:
        results: Dictionary mapping dataset names to success status
    """
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)

    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)

    dataset_names = {
        "hpo": "Human Phenotype Ontology (HPO)",
        "icd10": "ICD-10-CM Disease Codes",
        "disease_symptoms": "Disease-Symptom Datasets"
    }

    for dataset_key, success in results.items():
        status_icon = "✅" if success else "❌"
        name = dataset_names.get(dataset_key, dataset_key)
        status = "SUCCESS" if success else "FAILED"
        print(f"{status_icon} {name}: {status}")

    print(f"\n{'=' * 70}")
    print(f"📈 Overall Success Rate: {success_count}/{total_count}")
    print(f"{'=' * 70}")

    if success_count == total_count:
        print("\n🎉 All datasets downloaded successfully!")
        print("\n🔍 Next steps:")
        print("   1. Verify the downloaded files:")
        print("      python scripts/download_datasets/verify_datasets.py")
        print("\n   2. Process and index the datasets:")
        print("      python scripts/process_datasets/index_hpo.py")
        print("      python scripts/process_datasets/index_icd10.py")
        print("\n   3. Update the vector store with new data:")
        print("      python scripts/seed_data.py --use-new-datasets")
        print("\n   4. Test the integration:")
        print("      python scripts/test_api.py")
    elif success_count > 0:
        print(f"\n⚠️ Partial success: {success_count} out of {total_count} datasets downloaded")
        print("\n   Review the errors above and retry failed downloads")
    else:
        print("\n❌ All downloads failed")
        print("\n   Please check your internet connection and try again")
        print("   Some datasets may require additional setup (e.g., Kaggle API)")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Download all priority medical datasets for Doctor-Ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all priority datasets
  python download_all_priority.py

  # Download to custom directory
  python download_all_priority.py --output /path/to/datasets

  # Download only specific datasets
  python download_all_priority.py --datasets hpo icd10

  # Include optional HPO gene mapping files
  python download_all_priority.py --include-optional-hpo

  # Use Kaggle API for disease datasets
  python download_all_priority.py --use-kaggle
        """
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Base output directory (default: datasets/)"
    )

    parser.add_argument(
        "--datasets",
        "-d",
        nargs="+",
        choices=["hpo", "icd10", "disease_symptoms"],
        default=None,
        help="Specific datasets to download (default: all)"
    )

    parser.add_argument(
        "--include-optional-hpo",
        action="store_true",
        help="Include optional HPO gene mapping files"
    )

    parser.add_argument(
        "--use-kaggle",
        "-k",
        action="store_true",
        help="Use Kaggle API for disease datasets (requires setup)"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress header and summary output"
    )

    args = parser.parse_args()

    # Print header unless quiet mode
    if not args.quiet:
        print_header()
        print(f"\n⏳ Starting downloads...\n")

    # Download datasets
    results = download_all_datasets(
        base_output_dir=args.output,
        include_optional_hpo=args.include_optional_hpo,
        use_kaggle=args.use_kaggle,
        datasets_to_download=args.datasets
    )

    # Print summary unless quiet mode
    if not args.quiet:
        print_summary(results)

    # Exit with appropriate code
    all_success = all(results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
