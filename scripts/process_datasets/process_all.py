"""
Master script to process all medical datasets for Doctor-Ai.

This script runs the complete pipeline:
1. Filter HPO dataset
2. Filter ICD-10 dataset
3. Merge all datasets
4. Index in Qdrant (optional)

Usage:
    python scripts/process_datasets/process_all.py
    python scripts/process_datasets/process_all.py --skip-index  # Skip Qdrant indexing
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
import argparse

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class DatasetProcessor:
    """Master dataset processor."""

    def __init__(self, skip_index: bool = False):
        """
        Initialize the processor.

        Args:
            skip_index: Whether to skip Qdrant indexing
        """
        self.skip_index = skip_index
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "process_datasets"

    def run_script(self, script_name: str, args: List[str] = None) -> Tuple[bool, str]:
        """
        Run a processing script.

        Args:
            script_name: Name of the script (e.g., "filter_hpo.py")
            args: Additional arguments for the script

        Returns:
            Tuple of (success, output)
        """
        script_path = self.scripts_dir / script_name
        cmd = [sys.executable, str(script_path)]

        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            return success, output

        except Exception as e:
            return False, str(e)

    def print_step(self, step_num: int, total_steps: int, title: str):
        """Print step header."""
        print("\n" + "=" * 70)
        print(f"STEP {step_num}/{total_steps}: {title}")
        print("=" * 70 + "\n")

    def run(self) -> bool:
        """
        Run the complete processing pipeline.

        Returns:
            True if all steps successful
        """
        print("=" * 70)
        print("🏥 Doctor-Ai Dataset Processing Pipeline")
        print("=" * 70)
        print("\nThis script will:")
        print("  1. Filter HPO dataset for diagnostic relevance")
        print("  2. Filter ICD-10 dataset for common diseases")
        print("  3. Merge all datasets into unified format")

        if not self.skip_index:
            print("  4. Index in Qdrant vector database")
        else:
            print("  4. [SKIPPED] Qdrant indexing")

        print("\n" + "=" * 70)
        input("\nPress ENTER to continue or Ctrl+C to cancel...")

        total_steps = 3 if self.skip_index else 4
        results = {}

        # Step 1: Filter HPO
        self.print_step(1, total_steps, "Filter HPO Dataset")
        success, output = self.run_script("filter_hpo.py")
        print(output)
        results["filter_hpo"] = success

        if not success:
            print("\n❌ HPO filtering failed. Check the output above.")
            return False

        # Step 2: Filter ICD-10
        self.print_step(2, total_steps, "Filter ICD-10 Dataset")
        success, output = self.run_script("filter_icd10.py")
        print(output)
        results["filter_icd10"] = success

        if not success:
            print("\n❌ ICD-10 filtering failed. Check the output above.")
            return False

        # Step 3: Merge datasets
        self.print_step(3, total_steps, "Merge All Datasets")
        success, output = self.run_script("merge_all_datasets.py")
        print(output)
        results["merge"] = success

        if not success:
            print("\n❌ Dataset merging failed. Check the output above.")
            return False

        # Step 4: Index in Qdrant (optional)
        if not self.skip_index:
            self.print_step(4, total_steps, "Index in Qdrant")
            success, output = self.run_script("index_in_qdrant.py")
            print(output)
            results["index_qdrant"] = success

            if not success:
                print("\n⚠️ Qdrant indexing failed. You can run it manually later:")
                print("   python scripts/process_datasets/index_in_qdrant.py")

        # Print final summary
        print("\n" + "=" * 70)
        print("📊 PROCESSING PIPELINE COMPLETE!")
        print("=" * 70)

        print("\n✅ Summary:")
        for step, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   {step}: {status}")

        all_success = all(results.values())

        if all_success:
            print("\n🎉 All steps completed successfully!")
            print("\n📁 Output location:")
            print(f"   {self.project_root}/datasets/processed/")
            print("\n🔍 Next steps:")
            print("   • Review filtered data in datasets/processed/")
            print("   • Test the API: python scripts/test_api.py")
            print("   • Query diseases using the Doctor-Ai API")

            if self.skip_index:
                print("\n💡 To index in Qdrant later:")
                print("   python scripts/process_datasets/index_in_qdrant.py")
        else:
            print("\n⚠️ Some steps failed. Please review the output above.")

        return all_success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process all medical datasets for Doctor-Ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline (filter, merge, index)
  python process_all.py

  # Skip Qdrant indexing
  python process_all.py --skip-index

  # Run individual steps
  python filter_hpo.py
  python filter_icd10.py
  python merge_all_datasets.py
  python index_in_qdrant.py
        """
    )

    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip Qdrant indexing step"
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    processor = DatasetProcessor(skip_index=args.skip_index)
    success = processor.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
