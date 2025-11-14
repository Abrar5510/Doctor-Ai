"""
Download disease-symptom datasets from various sources.

Includes:
- Kaggle Disease Symptoms and Patient Profile Dataset
- Sample datasets from public repositories
- Disease-symptom mapping datasets

Dataset size: ~5MB (safe for GitHub)
"""

import os
import sys
import urllib.request
import json
import zipfile
from pathlib import Path
from typing import Optional, List, Dict
import csv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Public dataset URLs
DATASETS = {
    "symptom_disease": {
        "name": "Disease-Symptom Dataset",
        "url": "https://raw.githubusercontent.com/Kaggle/kaggle-api/main/examples/data/disease_symptom_data.csv",
        "fallback_url": "https://people.dbmi.columbia.edu/~friedma/Projects/DiseaseSymptomKB/index.html",
        "description": "Disease-symptom mapping dataset",
        "filename": "disease_symptom_data.csv",
        "method": "direct"
    },
}


def download_file(url: str, output_path: Path, description: str = "") -> bool:
    """
    Download a file with progress indication.

    Args:
        url: URL to download from
        output_path: Path to save the file
        description: Description of the file being downloaded

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n📥 Downloading: {description or output_path.name}")
        print(f"   URL: {url}")
        print(f"   Destination: {output_path}")

        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end="")
            else:
                downloaded_kb = downloaded / 1024
                print(f"\r   Downloaded: {downloaded_kb:.1f} KB", end="")

        urllib.request.urlretrieve(url, output_path, reporthook=report_progress)
        print()  # New line after progress

        # Verify file exists and has content
        if output_path.exists() and output_path.stat().st_size > 0:
            file_size = output_path.stat().st_size / 1024
            if file_size > 1024:
                print(f"   ✅ Downloaded successfully ({file_size/1024:.2f} MB)")
            else:
                print(f"   ✅ Downloaded successfully ({file_size:.2f} KB)")
            return True
        else:
            print(f"   ❌ Download failed or file is empty")
            return False

    except Exception as e:
        print(f"   ❌ Error downloading: {e}")
        return False


def download_kaggle_dataset(dataset_name: str, output_dir: Path) -> bool:
    """
    Download a dataset from Kaggle using the Kaggle API.

    Args:
        dataset_name: Kaggle dataset identifier (e.g., "username/dataset-name")
        output_dir: Directory to save the dataset

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if kaggle is installed
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi

        print(f"\n📥 Downloading from Kaggle: {dataset_name}")

        # Initialize API
        api = KaggleApi()
        api.authenticate()

        # Download dataset
        api.dataset_download_files(
            dataset_name,
            path=output_dir,
            unzip=True
        )

        print(f"   ✅ Downloaded successfully to {output_dir}")
        return True

    except ImportError:
        print(f"   ⚠️ Kaggle API not installed")
        print(f"   Install with: pip install kaggle")
        print(f"   Then setup credentials: https://github.com/Kaggle/kaggle-api#api-credentials")
        return False
    except Exception as e:
        print(f"   ❌ Error downloading from Kaggle: {e}")
        print(f"   Note: Ensure you have valid Kaggle API credentials")
        print(f"   Setup: https://github.com/Kaggle/kaggle-api#api-credentials")
        return False


def create_sample_dataset(output_path: Path) -> bool:
    """
    Create a sample disease-symptom dataset.

    Args:
        output_path: Path to save the sample dataset

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n📝 Creating sample disease-symptom dataset...")

        sample_data = [
            {
                "disease": "Common Cold",
                "symptoms": "runny nose, sneezing, sore throat, cough, congestion",
                "severity": "mild",
                "duration_days": "7-10",
                "frequency": "very_common"
            },
            {
                "disease": "Influenza",
                "symptoms": "fever, chills, muscle aches, cough, headache, fatigue",
                "severity": "moderate",
                "duration_days": "7-14",
                "frequency": "common"
            },
            {
                "disease": "Pneumonia",
                "symptoms": "cough, fever, difficulty breathing, chest pain, fatigue",
                "severity": "severe",
                "duration_days": "14-21",
                "frequency": "uncommon"
            },
            {
                "disease": "Hypothyroidism",
                "symptoms": "fatigue, weight gain, cold intolerance, constipation, dry skin",
                "severity": "moderate",
                "duration_days": "chronic",
                "frequency": "common"
            },
            {
                "disease": "Type 2 Diabetes",
                "symptoms": "increased thirst, frequent urination, fatigue, blurred vision, slow healing",
                "severity": "moderate",
                "duration_days": "chronic",
                "frequency": "very_common"
            },
            {
                "disease": "Migraine",
                "symptoms": "severe headache, nausea, sensitivity to light, visual disturbances",
                "severity": "moderate_to_severe",
                "duration_days": "1-3",
                "frequency": "common"
            },
            {
                "disease": "Hypertension",
                "symptoms": "often asymptomatic, headache, dizziness, shortness of breath",
                "severity": "mild_to_moderate",
                "duration_days": "chronic",
                "frequency": "very_common"
            },
            {
                "disease": "Gastroenteritis",
                "symptoms": "diarrhea, nausea, vomiting, abdominal pain, fever",
                "severity": "moderate",
                "duration_days": "3-7",
                "frequency": "common"
            },
            {
                "disease": "Asthma",
                "symptoms": "wheezing, shortness of breath, chest tightness, cough",
                "severity": "mild_to_severe",
                "duration_days": "chronic",
                "frequency": "common"
            },
            {
                "disease": "Urinary Tract Infection",
                "symptoms": "painful urination, frequent urination, lower abdominal pain, cloudy urine",
                "severity": "mild_to_moderate",
                "duration_days": "3-7",
                "frequency": "common"
            }
        ]

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)

        file_size = output_path.stat().st_size / 1024
        print(f"   ✅ Sample dataset created: {output_path} ({file_size:.2f} KB)")
        return True

    except Exception as e:
        print(f"   ❌ Error creating sample dataset: {e}")
        return False


def download_disease_symptoms(
    output_dir: Optional[str] = None,
    use_kaggle: bool = False,
    create_sample: bool = True
) -> bool:
    """
    Download disease-symptom datasets.

    Args:
        output_dir: Directory to save files (default: datasets/samples)
        use_kaggle: Whether to attempt Kaggle download
        create_sample: Whether to create a sample dataset

    Returns:
        True if at least one dataset was acquired successfully
    """
    # Set default output directory
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "datasets" / "samples"
    else:
        output_dir = Path(output_dir)

    print("=" * 70)
    print("🩺 Disease-Symptom Dataset Downloader")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Use Kaggle API: {use_kaggle}")
    print(f"Create sample dataset: {create_sample}")

    success_count = 0

    # Try Kaggle download if requested
    if use_kaggle:
        kaggle_success = download_kaggle_dataset(
            "uom190346a/disease-symptoms-and-patient-profile-dataset",
            output_dir
        )
        if kaggle_success:
            success_count += 1

    # Create sample dataset
    if create_sample:
        sample_path = output_dir / "disease_symptom_sample.csv"
        if create_sample_dataset(sample_path):
            success_count += 1

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Download Summary")
    print("=" * 70)

    if success_count > 0:
        print(f"\n✅ Successfully acquired {success_count} dataset(s)!")
        print(f"\n📁 Files saved to: {output_dir}")
        print("\n🔍 Next steps:")
        print("   1. Review the downloaded datasets")
        print("   2. Process and validate the data")
        print("   3. Integrate with your disease database")
        print("\n💡 Tips:")
        print("   - Use the sample dataset for initial testing")
        print("   - Install Kaggle API for access to larger datasets:")
        print("     pip install kaggle")
        print("   - Setup Kaggle credentials:")
        print("     https://github.com/Kaggle/kaggle-api#api-credentials")
        return True
    else:
        print("\n⚠️ No datasets were acquired.")
        print("   Try running with --use-kaggle after setting up Kaggle API")
        return False


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download disease-symptom datasets"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/samples)"
    )
    parser.add_argument(
        "--use-kaggle",
        "-k",
        action="store_true",
        help="Download from Kaggle (requires Kaggle API setup)"
    )
    parser.add_argument(
        "--no-sample",
        action="store_true",
        help="Skip creating sample dataset"
    )

    args = parser.parse_args()

    success = download_disease_symptoms(
        output_dir=args.output,
        use_kaggle=args.use_kaggle,
        create_sample=not args.no_sample
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
