#!/usr/bin/env python3

import sys
import subprocess
import yaml
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_symbols.py <symbol_directory>")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path("work") / f"{input_dir.name}-output"
    output_dir.mkdir(parents=True, exist_ok=True)

    with (Path(__file__).parent.parent / "db" / "pipeline.yaml").open('r') as f:
        config = yaml.safe_load(f)

    include = config.get("include", [])
    if not include:
        print("No files specified in config.")
        return

    print("Will handle the following:", include)

    for entry in include:
        name = Path(entry).with_suffix('')
        sym_file = input_dir / f"{name}.sym"
        csv_file = output_dir / f"{Path(entry)}.csv"

        (output_dir / Path(entry).parent).mkdir(parents=True, exist_ok=True)

        if not sym_file.is_file():
            print(f"Missing: {sym_file}")
            continue

        cmd = ["work/symread32", str(sym_file), "-o", str(csv_file)]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
