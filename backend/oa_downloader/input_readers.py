from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document

from .parse import normalize_text


def read_docx_refs(path: str) -> list[str]:
    doc = Document(path)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            lines.append(t)
    # Heuristic: treat each paragraph as a ref line; users often have one ref per paragraph.
    return [normalize_text(x) for x in lines]


def read_xlsx_refs(path: str) -> list[str]:
    # Read first sheet; collect all non-empty cells as possible refs.
    df = pd.read_excel(path, header=None)
    refs = []
    for v in df.values.ravel().tolist():
        if v is None:
            continue
        s = str(v).strip()
        if s:
            refs.append(normalize_text(s))
    return refs
