from __future__ import annotations

from pathlib import Path

from .config import sanitize_folder_name


def derive_run_dir(output_root: Path, input_file: str | None) -> Path:
    if input_file:
        base = sanitize_folder_name(Path(input_file).stem)
    else:
        base = "pasted"
    return output_root / base
