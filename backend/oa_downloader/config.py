from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    output_root: Path
    delay_seconds: float = 1.0
    retries: int = 3
    timeout_seconds: int = 30
    proxy: str | None = None
    resume: bool = False


def sanitize_folder_name(name: str) -> str:
    # Basic Windows-safe folder name sanitizer
    bad = '<>:"/\\|?*'
    out = ''.join('_' if c in bad else c for c in name)
    out = out.strip().strip('.')
    return out or 'output'


def ensure_dir(p: Path) -> None:
    os.makedirs(p, exist_ok=True)
