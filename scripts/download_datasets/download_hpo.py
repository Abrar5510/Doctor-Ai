"""
Download Human Phenotype Ontology (HPO) datasets.

The HPO provides a standardized vocabulary of phenotypic abnormalities
encountered in human disease. Essential for rare disease detection.

Dataset size: ~50MB (safe for GitHub)
"""

import os
import sys
import urllib.request
import hashlib
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# HPO GitHub Release URLs
HPO_RELEASES_BASE = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download"

HPO_FILES = {
    "hp.obo": {
        "url": f"{HPO_RELEASES_BASE}/hp.obo",
        "description": "Main HPO ontology file",
        "required": True,
    },
    "phenotype.hpoa": {
        "url": f"{HPO_RELEASES_BASE}/phenotype.hpoa",
        "description": "Disease-to-phenotype annotations",
        "required": True,
    },
    "genes_to_phenotype.txt": {
        "url": f"{HPO_RELEASES_BASE}/genes_to_phenotype.txt",
        "description": "Gene-to-phenotype mappings",
        "required": False,
    },
    "phenotype_to_genes.txt": {
        "url": f"{HPO_RELEASES_BASE}/phenotype_to_genes.txt",
        "description": "Phenotype-to-gene mappings",
        "required": False,
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


def verify_hpo_file(file_path: Path) -> bool:
    """
    Verify that an HPO file is valid.

    Args:
        file_path: Path to the file to verify

    Returns:
        True if valid, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines to check format
            lines = [f.readline() for _ in range(10)]

            if file_path.suffix == '.obo':
                # Check for OBO format header
                if any('format-version:' in line for line in lines):
                    return True
            elif file_path.suffix in ['.hpoa', '.txt']:
                # Check for tab-separated content
                if any('\t' in line for line in lines):
                    return True

        return False
    except Exception as e:
        print(f"   ⚠️ Validation error: {e}")
        return False


def download_hpo(output_dir: Optional[str] = None, include_optional: bool = False) -> bool:
    """
    Download HPO dataset files.

    Args:
        output_dir: Directory to save files (default: datasets/ontologies/hpo)
        include_optional: Whether to download optional files

    Returns:
        True if all required files downloaded successfully
    """
    # Set default output directory
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "datasets" / "ontologies" / "hpo"
    else:
        output_dir = Path(output_dir)

    print("=" * 70)
    print("🧬 HPO (Human Phenotype Ontology) Downloader")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print(f"Include optional files: {include_optional}")

    # Track download results
    results = {}

    # Download each file
    for filename, file_info in HPO_FILES.items():
        # Skip optional files if not requested
        if not include_optional and not file_info["required"]:
            print(f"\n⏭️  Skipping optional file: {filename}")
            continue

        output_path = output_dir / filename

        # Download the file
        success = download_file(
            url=file_info["url"],
            output_path=output_path,
            description=file_info["description"]
        )

        # Verify the file if download succeeded
        if success:
            if verify_hpo_file(output_path):
                print(f"   ✅ File validated successfully")
                results[filename] = "success"
            else:
                print(f"   ⚠️ File downloaded but validation failed")
                results[filename] = "validation_failed"
        else:
            results[filename] = "failed"

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Download Summary")
    print("=" * 70)

    success_count = sum(1 for r in results.values() if r == "success")
    total_count = len(results)

    for filename, result in results.items():
        status_icon = {
            "success": "✅",
            "validation_failed": "⚠️",
            "failed": "❌"
        }.get(result, "❓")

        print(f"{status_icon} {filename}: {result}")

    print(f"\n📈 Success rate: {success_count}/{total_count}")

    # Check if all required files succeeded
    all_required_success = all(
        results.get(name) == "success"
        for name, info in HPO_FILES.items()
        if info["required"]
    )

    if all_required_success:
        print("\n✅ All required HPO files downloaded successfully!")
        print(f"\n📁 Files saved to: {output_dir}")
        print("\n🔍 Next steps:")
        print("   1. Review the downloaded files")
        print("   2. Run: python scripts/process_datasets/index_hpo.py")
        print("   3. Integrate with Qdrant vector store")
        return True
    else:
        print("\n❌ Some required files failed to download.")
        print("   Please check your internet connection and try again.")
        return False


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download Human Phenotype Ontology (HPO) datasets"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: datasets/ontologies/hpo)"
    )
    parser.add_argument(
        "--include-optional",
        "-i",
        action="store_true",
        help="Download optional gene mapping files"
    )

    args = parser.parse_args()

    success = download_hpo(
        output_dir=args.output,
        include_optional=args.include_optional
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
