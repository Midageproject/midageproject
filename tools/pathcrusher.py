#!/usr/bin/env python3

import sys
import re
from ruamel.yaml import YAML
import csv
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <sym directory>")
        sys.exit(1)

    yaml = YAML(typ='rt')

    pipeline_path = Path(__file__).parent.parent / "db" / "pipeline.yaml"
    with pipeline_path.open('r', encoding='utf-8') as f:
        config = yaml.load(f)

    input_dir = Path(sys.argv[1])
    db_path = Path(__file__).parent.parent / "db" / "components"

    # Compile regex pattern for matching file paths
    for component in config.get('include', []):
        comp_name = Path(component).with_suffix('')
        sym_file = input_dir / f"{comp_name}.sym"
        yaml_file = db_path / f"{Path(component)}.yaml"
        bin_file = input_dir / f"{component}"
        
        
        # Read and process symbol file
        paths = set()

        cmd_fmt = (
        'strings "{}" | '
        'grep -Eio "[./\\\\]{{0,2}}[a-z0-9_./\\\\-]{{2,}}\\.(c|cpp|asm|h|inc)" | '
        'sed -e \'s|\\\\|/|g\' -e \'s|^\\.?/||\' -e \'s|^\\.?\\./||\' -e \'s|//*|/|g\' | '
        'grep -vE \'^-+\' | '
        'sort -u'
        )
               
        if sym_file.is_file():
            exec = subprocess.run(cmd_fmt.format(sym_file), shell=True, stdout=subprocess.PIPE, text=True)
            paths = exec.stdout.strip().splitlines()
        else:
            print(f"Missing: {sym_file}")
            continue

        if bin_file.is_file():
            print(f"Binary found for {component}, will try extracting paths")
            exec = subprocess.run(cmd_fmt.format(bin_file), shell=True, stdout=subprocess.PIPE, text=True)
            new_paths = exec.stdout.strip().splitlines()
            old_set = set(paths)
            for p in new_paths:
             if p not in old_set:
                paths.append(p)
                old_set.add(p)

        if not yaml_file.is_file():
            print(f"Missing YAML file: {yaml_file}")
            continue

        with yaml_file.open('r', encoding='utf-8') as f:
            data = yaml.load(f)

        # Update appearances
        current_version = input_dir.stem.split('-', 1)[0]
        updated = False
        for appearance in data['appearances']:
            if appearance['version'] == current_version:
                tree = appearance.get('source_tree', [])
                if any(isinstance(i, list) for i in tree):
                    # flatten if needed
                    tree = [item for sublist in tree for item in (sublist if isinstance(sublist, list) else [sublist])]
                    appearance['source_tree'] = tree
                    
                new_paths = [p for p in paths if p not in tree]
                if new_paths:
                    tree.extend(new_paths)
                    appearance['source_tree'] = tree
                    updated = True
                break

        if updated:
            with yaml_file.open('w', encoding='utf-8') as f:
                yaml.dump(data, f)
            print(f"Updated: {yaml_file}")
        else:
            print(f"No changes for: {yaml_file}")

if __name__ == "__main__":
    main()