#!/usr/bin/env python3

import sys
import subprocess
from jinja2 import Environment
from ruamel.yaml import YAML
import csv
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict

@dataclass
class Symbol:
    name: str
    demangled: str
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

    yaml = YAML(typ='rt')
    with (Path(__file__).parent.parent / "db" / "pipeline.yaml").open('r', encoding='utf-8') as f:
        config = yaml.load(f)

    input_dir = Path(sys.argv[1])
    template_path = Path(__file__).parent / "component.j2"
    db_path = Path(__file__).parent.parent / "db" / "components"
    template_text = template_path.read_text(encoding="utf-8")

    env = Environment(trim_blocks=True, lstrip_blocks=True)
    template = env.from_string(template_text)

    for file in config['include']:
        name = Path(file)
        csv_file = input_dir / f"{name}.csv"

        if not csv_file.is_file():
            print(f"Missing: {csv_file}")
            continue

        binname = Path(file).stem.upper()

        
        data = Entry(filename=file, binary=binname)
        version_dir = input_dir.stem.split('-', 1)[0]
        if 'versions' not in config:
           config['versions'] = []

        if version_dir not in config['versions']:
          config['versions'].append(str(version_dir))
          with (Path(__file__).parent.parent / "db" / "pipeline.yaml").open("w", encoding="utf-8") as f:
           yaml.dump(config, f)
        
        appearance = Appearance(version=version_dir)


        with csv_file.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            segment_data = defaultdict(lambda: defaultdict(list))
            for row in reader:
                segment_data[row['SegmentNumber']][row['SegmentOffset']].append(row)

            for seg_num, offsets in segment_data.items():
                for seg_offset, rows in offsets.items():
                    segment = Segment(num=seg_num, name=rows[0]['SegmentName'], offset=seg_offset)
                    for row in rows:
                        if (Path(__file__).parent / "demumble/demumble").exists():
                           necromancer = "tools/demumble/demumble"
                        cmd = [ necromancer or "work/undname", row['SymbolName']]
                        demangled = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                        stdout, _ = demangled.communicate()
                        processed_name = stdout.decode().strip()
                        segment.symbols.append(Symbol(
                            name=row['SymbolName'],
                            demangled=processed_name if processed_name != row['SymbolName'] else "",
                            offset=row['SymbolOffset']
                        ))
                    appearance.segments.append(segment)
        data.appearances.append(appearance)

        rendered = template.render(data=data)
        db_path.mkdir(parents=True, exist_ok=True)
        db_file = db_path / f"{file}.yaml"

        if not db_file.is_file():
            db_file.parent.mkdir(parents=True, exist_ok=True)
            with db_file.open("w", encoding='utf-8') as f:
                f.write(rendered)
        else:
            if db_file.is_file:
                with db_file.open("r+", encoding='utf-8') as f:
                    existing = yaml.load(f)
                    versions = [a['version'] for a in existing.get('appearances', [])]
                    if str(version_dir) not in versions:
                        existing['appearances'].append(asdict(appearance))
                        f.seek(0)
                        f.truncate()
                        yaml.dump(existing, f)
                        
if __name__ == "__main__":
    main()