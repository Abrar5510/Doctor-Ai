"""
Download ICD-10-CM (International Classification of Diseases, 10th Revision) datasets.

ICD-10-CM is the standard for disease classification in the United States.
Essential for diagnostic coding and disease categorization.

Dataset size: ~50MB (safe for GitHub)
"""

import os
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict
import csv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# CDC ICD-10-CM URLs (2024 version)
ICD10_BASE_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2024"

ICD10_FILES = {
    "codes": {
        "url": f"{ICD10_BASE_URL}/icd10cm-codes-2024.zip",
        "description": "ICD-10-CM diagnosis codes",
        "extract": True,
    },
    "tabular": {
        "url": f"{ICD10_BASE_URL}/icd10cm-tabular-2024.xml",
        "description": "ICD-10-CM tabular list (XML)",
        "extract": False,
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

        urllib.request.urlretrieve(url, output_path, reporthook=report_progress)
        print()  # New line after progress

        # Verify file exists and has content
        if output_path.exists() and output_path.stat().st_size > 0:
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Downloaded successfully ({file_size:.2f} MB)")
            return True
        else:
            print(f"   ❌ Download failed or file is empty")
            return False

    except Exception as e:
        print(f"   ❌ Error downloading: {e}")
        return False


def extract_zip(zip_path: Path, output_dir: Path) -> bool:
    """
    Extract a ZIP file.

    Args:
        zip_path: Path to ZIP file
        output_dir: Directory to extract to

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n📦 Extracting: {zip_path.name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        print(f"   ✅ Extracted to: {output_dir}")
        return True

    except Exception as e:
        print(f"   ❌ Error extracting: {e}")
        return False


def parse_icd10_codes(codes_file: Path) -> List[Dict[str, str]]:
    """
    Parse ICD-10-CM codes file.

    Args:
        codes_file: Path to codes text file

    Returns:
        List of dictionaries containing code information
    """
    codes = []

    try:
        with open(codes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    # ICD-10 format: code followed by description
                    # Example: "A00.0 Cholera due to Vibrio cholerae 01, biovar cholerae"
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        code, description = parts
                        codes.append({
                            "code": code,
                            "description": description.strip(),
                            "category": code[:3],  # First 3 characters
                            "subcategory": code[3:] if len(code) > 3 else ""
                        })

        print(f"   ✅ Parsed {len(codes)} ICD-10-CM codes")
        return codes

    except Exception as e:
        print(f"   ❌ Error parsing codes: {e}")
        return []


def create_csv_export(codes: List[Dict[str, str]], output_path: Path) -> bool:
    """
    Create a CSV export of ICD-10 codes.

    Args:
        codes: List of code dictionaries
        output_path: Path to save CSV file

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n💾 Creating CSV export...")

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if codes:
                writer = csv.DictWriter(f, fieldnames=codes[0].keys())
                writer.writeheader()
                writer.writerows(codes)

        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ CSV created: {output_path} ({file_size:.2f} MB)")
        return True

    except Exception as e:
        print(f"   ❌ Error creating CSV: {e}")
        return False


def download_icd10(output_dir: Optional[str] = None, create_csv: bool = True) -> bool:
    """
    Download ICD-10-CM dataset files.

    Args:
        output_dir: Directory to save files (default: datasets/ontologies/icd10)
        create_csv: Whether to create a CSV export of codes

    Returns:
        True if all files downloaded successfully
    """
    # Set default output directory
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "datasets" / "ontologies" / "icd10"
    else:
        output_dir = Path(output_dir)

    print("=" * 70)
    print("🏥 ICD-10-CM Downloader")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Create CSV export: {create_csv}")

    # Track download results
    results = {}
    all_codes = []

    # Download each file
    for file_key, file_info in ICD10_FILES.items():
        filename = file_info["url"].split("/")[-1]
        output_path = output_dir / filename

        # Download the file
        success = download_file(
            url=file_info["url"],
            output_path=output_path,
            description=file_info["description"]
        )

        if success:
            results[file_key] = "success"

            # Extract if it's a ZIP file
            if file_info["extract"] and output_path.suffix == ".zip":
                extract_success = extract_zip(output_path, output_dir)
                if extract_success:
                    # Try to find and parse the codes file
                    for extracted_file in output_dir.glob("*.txt"):
                        if "order" in extracted_file.name.lower() or "code" in extracted_file.name.lower():
                            codes = parse_icd10_codes(extracted_file)
                            all_codes.extend(codes)
        else:
            results[file_key] = "failed"

    # Create CSV export if requested and codes were found
    if create_csv and all_codes:
        csv_path = output_dir / "icd10cm_codes_2024.csv"
        create_csv_export(all_codes, csv_path)

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Download Summary")
    print("=" * 70)

    success_count = sum(1 for r in results.values() if r == "success")
    total_count = len(results)

    for file_key, result in results.items():
        status_icon = "✅" if result == "success" else "❌"
        print(f"{status_icon} {file_key}: {result}")

    print(f"\n📈 Success rate: {success_count}/{total_count}")

    if all_codes:
        print(f"\n📋 Total ICD-10-CM codes: {len(all_codes)}")

    if success_count == total_count:
        print("\n✅ All ICD-10-CM files downloaded successfully!")
        print(f"\n📁 Files saved to: {output_dir}")
        print("\n🔍 Next steps:")
        print("   1. Review the downloaded files")
        print("   2. Use icd10cm_codes_2024.csv for easy integration")
        print("   3. Map ICD-10 codes to your disease database")
        return True
    else:
        print("\n❌ Some files failed to download.")
        print("   Please check your internet connection and try again.")
        return False


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download ICD-10-CM (International Classification of Diseases) datasets"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/ontologies/icd10)"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip CSV export creation"
    )

    args = parser.parse_args()

    success = download_icd10(
        output_dir=args.output,
        create_csv=not args.no_csv
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
