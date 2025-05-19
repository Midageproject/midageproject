#!/usr/bin/env python3

import sys
import subprocess
import yaml
import shutil
from pathlib import Path
from itertools import chain



special_includes = {
        "MSACM.H": "MMREG.H",
        "MSACMDRV.H": "MSACM.H"
}

def resolve_includes(header_name, include_map):
    includes = []
    seen = set()

    def normalize(name):
        name = name.upper()
        for prefix in ("INC_WIN98_INC_", "INC_WIN98_"):
            if name.startswith(prefix):
                return name[len(prefix):]
        return name

    def visit(h):
        key = normalize(h)
        if key in seen:
            return
        seen.add(key)
        if key in include_map:
            visit(include_map[key])
            includes.append(include_map[key])

    visit(header_name)
    return includes

def normalize_name(name):
    if name.upper().startswith("INC_WIN98_INC16_"):
            return name[len("INC_WIN98_INC16_"):]
    if name.upper().startswith("INC_WIN98_"):
            return name[len("INC_WIN98_"):]
    return name

# I aint gonna use msvc just for this
def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_symbols.py <symbol_directory>")
        sys.exit(1)

    input_dir = Path(sys.argv[1]).resolve()
    base_output_dir = Path("work") / f"{input_dir.name}-inc-output"
    flat_output_dir = Path("work") / f"{input_dir.name}-inc-normalized"
    wdf_inc = input_dir.parent / "inc"

    base_output_dir.mkdir(parents=True, exist_ok=True)
    flat_output_dir.mkdir(parents=True, exist_ok=True)

    with (Path(__file__).parent.parent / "db" / "pipeline.yaml").open("r") as f:
        config = yaml.safe_load(f)

    header_files = list(input_dir.rglob("*.h")) + list(input_dir.rglob("*.H"))

    for header in chain(wdf_inc.rglob("*.h"), wdf_inc.rglob("*.H"), wdf_inc.rglob("*.inl")):
        dst = flat_output_dir /  normalize_name(header.name).lower()
        dst1 = flat_output_dir / normalize_name(header.name)
        dst.parent.mkdir(exist_ok=True)
        shutil.copyfile(header, dst)
        shutil.copyfile(header, dst1)
    
    for header in header_files:
        dst = flat_output_dir / normalize_name(header.name)
        dst1 = flat_output_dir / normalize_name(header.name).lower()
        shutil.copyfile(header, dst)
        shutil.copyfile(header, dst1)
         
         
    for staged in flat_output_dir.rglob("*.h"):
        rel_path = staged.relative_to(flat_output_dir)
        out_file = base_output_dir / rel_path.with_suffix(".i")
        out_file.parent.mkdir(parents=True, exist_ok=True)

        normalized_name = normalize_name(staged.name)
        flat_file = flat_output_dir / normalized_name.replace(".H", ".i").replace(".h", ".i")
        cmd = [
            "clang", "-E", "-P", "-nostdinc",
            "-D__STDC__",
            "-I", str(flat_output_dir),
            "-D_WIN32", "-D_M_IX86", "-D__cplusplus", "-D_X86_" "-D_M_IX86", "-D_MSC_VER=3000", "-D_PREFAST_", "-D__midl", "-DSAL_NO_ATTRIBUTE_DECLARATIONS",
        ]

        required_includes = resolve_includes(staged.name.upper(), special_includes)
        for inc in required_includes:
            cmd += ["-include", inc]

        cmd.append(str(staged))

        print(f"[Preprocess] {' '.join(cmd)} → {out_file.name} / {flat_file.name}")

        with open(out_file, "w") as out:
            try:
                subprocess.run(cmd, check=True, stdout=out)
            except Exception as e:
                print(e)
                continue
            
if __name__ == "__main__":
    main()
