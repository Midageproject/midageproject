# win9x-symbol-docs

Reverse-engineered documentation of the Windows 95/98/Me source tree, built from publicly available debug symbols.

This is **not** a leak, dump, or decompilation of any proprietary code. It’s a clean-room effort to map out the internal structure of Windows 9x using legal and publicly released symbol data from MSDN and SDKs.

## What’s in here

- **Module layout**: Overview of core components like `KRNL386.EXE`, `VMM32.VXD`, and userland modules (`USER.EXE`, `GDI.EXE`, etc.)
- **Function listings**: Indexed exports, internal entry points, and thunk layers with context where available.
- **Segment mapping**: Code and data segment structure with annotation (especially for 16-bit modules).
- **Naming conventions**: Observed naming patterns from debug info, useful for cross-referencing with system binaries and existing documentation.

## Goals

- Help OS developers, retrocomputing enthusiasts, and reverse engineers understand the architecture of Windows 9x.
- Provide a clear, organized reference for the symbol data that already exists but is mostly unstructured.
- Preserve legacy system knowledge without infringing on IP.

## What this is not

- Not an attempt to reimplement or clone Windows 9x.
- Not a source code drop or disassembly dump.
- Not affiliated with Microsoft.

## How it works

- Symbol files (`.dbg`, `.sym`, `.pdb`) from public sources are parsed and normalized.
- The result is structured into placeholders and JSON (in future) for scripting or search purposes.
- Where possible, references to SDK headers (Win16, DDK, etc.) are made to clarify context.

## Contributions

PRs welcome. If you've got more symbols, clearer offsets, or notes from historical sources (MSDN CDs, old SDKs, etc.), feel free to open an issue or submit improvements.

## License

MIT for the documentation and tooling. Symbols are attributed to their original source and are used for educational/documentation purposes.

---


