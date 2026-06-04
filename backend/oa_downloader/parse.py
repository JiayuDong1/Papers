from __future__ import annotations

import re


def split_references(text: str) -> list[str]:
    # Heuristic: split on blank lines; also handle numbered lists.
    blocks = re.split(r"\n\s*\n+", text.strip(), flags=re.M)
    refs = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        refs.append(b)
    return refs


def normalize_text(s: str) -> str:
    # Normalize fullwidth punctuation and whitespace; keep CJK.
    s = s.replace('，', ',').replace('。', '.').replace('：', ':').replace('（', '(').replace('）', ')')
    s = re.sub(r"\s+", " ", s).strip()
    return s


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)


def extract_doi(s: str) -> str | None:
    m = DOI_RE.search(s)
    return m.group(0) if m else None
