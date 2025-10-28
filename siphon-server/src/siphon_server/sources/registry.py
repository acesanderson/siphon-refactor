from pathlib import Path
from xdg_base_dirs import xdg_data_home
import re
import json

DIR_PATH = Path(__file__).parent
DIRECTORIES = [d for d in DIR_PATH.iterdir() if d.is_dir()]
REGISTRY_FILE = xdg_data_home() / "siphon" / "registry.json"


def validate_directory(directory: Path) -> str:
    """
    Go through a checklist:
    /parser.py should have a class named *Parser (store * for later, match (.+)Parser)
    /extractor.py should have a class named *Extractor (store * for later, match (.+)Extractor)
    /enricher.py should have a class named *Enricher (store * for later, match (.+)Enricher)
    $1 should be the same for all three classes
    $1.lower() should == directory name

    Return the class name; raise an exception if any check fails.
    """
    dir_name = directory.name
    parser_file = directory / "parser.py"
    extractor_file = directory / "extractor.py"
    enricher_file = directory / "enricher.py"

    # Verify the files exist
    for file in [parser_file, extractor_file, enricher_file]:
        if not file.exists():
            raise FileNotFoundError(f"Missing file: {file}")

    # Find class names in the files
    def find_class_name(file: Path, suffix: str) -> str | None:
        with file.open("r") as f:
            for line in f:
                line = line.strip()
                match = re.match(rf"class (.+){suffix}\b", line)
                if match:
                    return match.group(1)

    parser_class = find_class_name(parser_file, "Parser")
    extractor_class = find_class_name(extractor_file, "Extractor")
    enricher_class = find_class_name(enricher_file, "Enricher")
    if not parser_class or not extractor_class or not enricher_class:
        raise ValueError(f"Could not find class definitions in {directory}")
    if not (parser_class == extractor_class == enricher_class):
        raise ValueError(f"Class names do not match in {directory}")
    if parser_class.lower() != dir_name:
        raise ValueError(f"Class name and directory name mismatch in {directory}")
    return parser_class


def generate_registry() -> None:
    """
    Validate all directories and generate registry.json
    """
    pipelines: list[str] = []
    for directory in DIRECTORIES:
        try:
            class_name = validate_directory(directory)
            pipelines.append(class_name)
            print(f"Validated {directory.name}: {class_name}")
        except Exception as e:
            print(f"Validation failed for {directory.name}: {e}")
    json_dict = {"pipelines": pipelines}
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _ = REGISTRY_FILE.write_text(json.dumps(json_dict, indent=4))
    print(f"Wrote registry to {REGISTRY_FILE}")


def load_registry() -> list[str]:
    """
    Load and return the list of pipelines from registry.json
    """
    if not REGISTRY_FILE.exists():
        generate_registry()
        assert REGISTRY_FILE.exists(), "Registry file was not created."
    content = REGISTRY_FILE.read_text()
    data = json.loads(content)
    return data.get("pipelines", [])


def main():
    generate_registry()


if __name__ == "__main__":
    main()
