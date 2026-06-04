from __future__ import annotations

from pathlib import Path


def derive_run_dir(output_root: Path, input_file: str | None) -> Path:
    if input_file:
        base = Path(input_file).stem
    else:
        base = "pasted"
    return output_root / base
