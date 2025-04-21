#!/usr/bin/env python3

import sys
import subprocess
from jinja2 import Environment
import ruamel.yaml as YAML
import csv
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

@dataclass
class Symbol:
    name: str
    offset: str

@dataclass
class Segment:
    num: str
    name: str
    offset: str
    symbols: list[Symbol] = field(default_factory=list)

@dataclass
class Appearance:
    version: str
    source_tree: list[str] = field(default_factory=list)
    segments: list[Segment] = field(default_factory=list)

@dataclass
class Entry:
    filename: str
    binary: str
    description: str = ""
    note: str = ""
    appearances: list[Appearance] = field(default_factory=list)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv directory>")
        sys.exit(1)

    yaml = YAML.YAML(typ='rt')
    with (Path(__file__).parent.parent / "db" / "pipeline.yaml").open('r', encoding='utf-8') as f:
        config = yaml.load(f)

    input_dir = Path(sys.argv[1])
    template_path = Path(__file__).parent / "component.j2"
    db_path = Path(__file__).parent.parent / "db" / "components"
    template_text = template_path.read_text(encoding="utf-8")

    env = Environment(trim_blocks=True, lstrip_blocks=True)
    template = env.from_string(template_text)

    for file in config['include']:
        name = Path(file).with_suffix('')
        csv_file = input_dir / f"{name}.csv"

        if not csv_file.is_file():
            print(f"Missing: {csv_file}")
            continue

        data = Entry(filename=file, binary=str(name).upper())
        appearance = Appearance(version=input_dir.stem.split('-', 1)[0])

        with csv_file.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            segment_data = defaultdict(lambda: defaultdict(list))
            for row in reader:
                segment_data[row['SegmentNumber']][row['SegmentOffset']].append(row)

            for seg_num, offsets in segment_data.items():
                for seg_offset, rows in offsets.items():
                    segment = Segment(num=seg_num, name=rows[0]['SegmentName'], offset=seg_offset)
                    for row in rows:
                        segment.symbols.append(Symbol(name=row['SymbolName'], offset=row['SymbolOffset']))
                    appearance.segments.append(segment)

        data.appearances.append(appearance)

        rendered = template.render(data=data)
        db_path.mkdir(parents=True, exist_ok=True)
        db_file = db_path / f"{file}.yaml"

        if not db_file.is_file():
            with db_file.open("w", encoding='utf-8') as f:
                f.write(rendered)
        else:
            with db_file.open("r", encoding='utf-8') as f:
                existing = yaml.load(f)
                versions = [a['version'] for a in existing.get('appearances', [])]
                if input_dir.stem not in versions:
                    print(f"[WARN] Version {input_dir.stem} missing in {db_file}, consider merging manually.")

if __name__ == "__main__":
    main()