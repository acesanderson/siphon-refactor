"""
Scaffold a new source type for Siphon.

Usage:
    python scripts/scaffold_source.py Reddit
    python scripts/scaffold_source.py GitHub
"""

import argparse
from pathlib import Path

DIR_PATH = Path(__file__).parent.resolve()
SOURCE_DIR = Path(
    "~/Brian_Code/siphon/siphon-server/src/siphon_server/sources"
).expanduser()
TEMPLATES_DIR = DIR_PATH / "templates"
PARSER_TEMPLATE = (TEMPLATES_DIR / "parser_template.txt").read_text()
EXTRACTOR_TEMPLATE = (TEMPLATES_DIR / "extractor_template.txt").read_text()
ENRICHER_TEMPLATE = (TEMPLATES_DIR / "enricher_template.txt").read_text()
INIT_TEMPLATE = (TEMPLATES_DIR / "init_template.txt").read_text()
TEST_TEMPLATE = (TEMPLATES_DIR / "test_template.txt").read_text()
TEST_CONFTEST_TEMPLATE = (TEMPLATES_DIR / "test_conftest_template.txt").read_text()


def validate_source_name(source_name: str):
    """
    Source name should be alphabetic, capialized, and one word.
    """
    if not source_name.isalpha():
        raise ValueError("Error: Source name must be alphabetic")
    if not source_name[0].isupper():
        raise ValueError("Error: Source name must start with a capital letter")


def generate_directories(source_name: str, dry_run: bool = True):
    source_name_lower = source_name.lower()
    base_dir = SOURCE_DIR / source_name_lower
    test_dir = base_dir / "tests"
    if dry_run:
        print(f"\n[DRY RUN] Would create the following directories:\n")
        print(f"  {base_dir}")
        print(f"  {test_dir}\n")
    else:
        base_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)


def generate_parser(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    content = PARSER_TEMPLATE.format(
        source_name=source_name,
    )
    file_path = SOURCE_DIR / source_lower / "parser.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: Parser file already exists: {file_path}")


def generate_extractor(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    content = EXTRACTOR_TEMPLATE.format(
        source_name=source_name,
    )
    file_path = SOURCE_DIR / source_lower / "extractor.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: Extractor file already exists: {file_path}")


def generate_enricher(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    content = ENRICHER_TEMPLATE.format(
        source_name=source_name,
    )
    file_path = SOURCE_DIR / source_lower / "enricher.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: Enricher file already exists: {file_path}")


def generate_init(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    content = INIT_TEMPLATE.format(
        source_name=source_name,
        source_lower=source_lower,
    )
    file_path = SOURCE_DIR / source_lower / "__init__.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: __init__.py file already exists: {file_path}")


def generate_tests(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    source_upper = source_name.upper()
    content = TEST_TEMPLATE.format(
        source_name=source_name,
        source_lower=source_lower,
        source_upper=source_upper,
    )
    file_path = SOURCE_DIR / source_lower / "tests" / f"test_{source_lower}.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: Test file already exists: {file_path}")


def generate_conftest(source_name: str, dry_run: bool = True):
    source_lower = source_name.lower()
    content = TEST_CONFTEST_TEMPLATE.format(
        source_name=source_name,
        source_lower=source_lower,
    )
    file_path = SOURCE_DIR / source_lower / "tests" / "conftest.py"
    if dry_run:
        print(f"[DRY RUN] Would create file: {file_path}\n")
        return
    else:
        if not file_path.exists():
            file_path.write_text(content)
            print(f"✓ Created: {file_path}")
        else:
            print(f"Error: conftest.py file already exists: {file_path}")


def scaffold(source_name: str, dry_run: bool = True):
    """
    Wrapper function to scaffold a new source type.
    """
    validate_source_name(source_name)
    generate_directories(source_name, dry_run)
    generate_parser(source_name, dry_run)
    generate_extractor(source_name, dry_run)
    generate_enricher(source_name, dry_run)
    generate_init(source_name, dry_run)
    generate_tests(source_name, dry_run)
    generate_conftest(source_name, dry_run)


def undo_scaffold(source_name: str):
    """
    Remove the scaffolded source type directory.
    First, print the files and directories that would be removed.
    Then, ask for confirmation before deleting.
    """
    source_lower = source_name.lower()
    base_dir = SOURCE_DIR / source_lower
    if not base_dir.exists():
        print(f"Error: Source directory does not exist: {base_dir}")
        return
    print(f"The following files and directories will be removed:\n")
    for path in base_dir.rglob("*"):
        print(f"  {path}")
    confirm = input(
        f"\nAre you sure you want to delete the entire directory '{base_dir}'? (y/n): "
    )
    if confirm.lower() == "y":
        for path in sorted(base_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        base_dir.rmdir()
        print(f"✓ Removed: {base_dir}")
    else:
        print("Aborted. No files were removed.")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new source type for Siphon."
    )
    parser.add_argument("source_name", type=str, help="Name of the new source type")
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the scaffold by removing the created files",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually create files instead of dry run",
    )
    args = parser.parse_args()
    dry_run = not args.no_dry_run
    if args.undo:
        undo_scaffold(args.source_name)
    else:
        scaffold(args.source_name, dry_run=dry_run)


if __name__ == "__main__":
    main()
