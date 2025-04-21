#!/usr/bin/env python3

import sys
import re
from ruamel.yaml import YAML
import csv
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv directory>")
        sys.exit(1)

    yaml = YAML(typ='rt')

    pipeline_path = Path(__file__).parent.parent / "db" / "pipeline.yaml"
    with pipeline_path.open('r', encoding='utf-8') as f:
        config = yaml.load(f)

    input_dir = Path(sys.argv[1])
    db_path = Path(__file__).parent.parent / "db" / "components"

    # Compile regex pattern for matching file paths
    pattern = re.compile(r'[./\\]{1,2}[a-z0-9_./\\-]{2,}\.(c|cpp|asm|h|inc)', re.IGNORECASE)

    for component in config.get('include', []):
        comp_name = Path(component).with_suffix('')
        sym_file = input_dir / f"{comp_name}.sym"
        yaml_file = db_path / f"{Path(component)}.yaml"

        if not sym_file.is_file():
            print(f"Missing: {sym_file}")
            continue

        # Read and process symbol file
        paths = set()
        with sym_file.open('rb') as f:
            data = f.read()
            data = data.decode('latin1', errors='ignore')
            for line in data:
                if pattern.search(line):
                    cleaned = line.strip().replace('\\', '/')
                    if cleaned.startswith('./'):
                        cleaned = cleaned[2:]
                    elif cleaned.startswith('../'):
                        cleaned = cleaned[3:]
                    paths.add(cleaned)
                    print(cleaned)

        if not yaml_file.is_file():
            print(f"Missing YAML file: {yaml_file}")
            continue

        with yaml_file.open('r', encoding='utf-8') as f:
            data = yaml.load(f)

        # Update appearances
        current_version = input_dir.stem
        updated = False
        for appearance in data.get('appearances', []):
            if appearance.get('version') == current_version:
                tree = appearance.get('tree', [])
                if isinstance(tree, list):
                    # Avoid duplicates
                    new_paths = [p for p in paths if p not in tree]
                    if new_paths:
                        tree.extend(new_paths)
                        appearance['tree'] = tree
                        updated = True
                else:
                    print(f"Warning: 'tree' is not a list in {yaml_file}")
                break
            updated = True

        if updated:
            with yaml_file.open('w', encoding='utf-8') as f:
                yaml.dump(data, f)
            print(f"Updated: {yaml_file}")
        else:
            print(f"No changes for: {yaml_file}")

if __name__ == "__main__":
    main()
