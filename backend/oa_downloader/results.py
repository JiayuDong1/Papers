from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd


RESULT_COLUMNS = [
    "input_reference",
    "title",
    "authors",
    "venue",
    "year",
    "doi",
    "pdf_url",
    "official_url",
    "status",
    "error",
    "output_pdf_path",
]


def load_previous_results(results_path: Path) -> pd.DataFrame | None:
    if not results_path.exists():
        return None
    try:
        df = pd.read_excel(results_path)
        return df
    except Exception:
        return None


def write_results(results_path: Path, rows: list[dict]) -> None:
    df = pd.DataFrame(rows)
    for c in RESULT_COLUMNS:
        if c not in df.columns:
            df[c] = None
    df = df[RESULT_COLUMNS]

    results_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(results_path, index=False)
