from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResolvedPaper:
    title: str | None = None
    authors: str | None = None
    venue: str | None = None
    year: int | None = None
    doi: str | None = None
    pdf_url: str | None = None
    official_url: str | None = None


def resolve_paper(_reference: str) -> ResolvedPaper:
    """Resolve a reference into metadata and OA links.

    Placeholder implementation for scaffolding.
    Next steps:
    - Try extract DOI from the reference
    - If DOI, use Crossref to fetch metadata and official URL
    - Use Unpaywall or other OA sources to find PDF URL
    - If no DOI, search by title/author/year (Crossref works)
    """
    return ResolvedPaper()
