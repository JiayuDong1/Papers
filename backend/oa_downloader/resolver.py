from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import quote

import requests

from .parse import extract_doi


@dataclass
class ResolvedPaper:
    title: str | None = None
    authors: str | None = None
    venue: str | None = None
    year: int | None = None
    doi: str | None = None
    pdf_url: str | None = None
    official_url: str | None = None


YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.I)
    d = d.lower()
    return d or None


def _extract_year(reference: str) -> int | None:
    years = [int(m.group(0)) for m in YEAR_RE.finditer(reference)]
    if not years:
        return None
    # Prefer the last year token in bibliography lines.
    return years[-1]


def _norm_text(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _crossref_headers() -> dict[str, str]:
    return {"User-Agent": "oa-pdf-downloader/0.1 (mailto:unknown@example.com)"}


def _extract_crossref_metadata(item: dict) -> ResolvedPaper:
    title_list = item.get("title") or []
    title = title_list[0].strip() if title_list else None

    authors = item.get("author") or []
    author_names = []
    for a in authors:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        n = f"{given} {family}".strip()
        if n:
            author_names.append(n)

    venue_list = item.get("container-title") or []
    venue = venue_list[0].strip() if venue_list else None

    year = None
    issued = item.get("issued", {}).get("date-parts") or []
    if issued and isinstance(issued[0], list) and issued[0]:
        try:
            year = int(issued[0][0])
        except Exception:
            year = None

    doi = _norm_doi(item.get("DOI"))
    official_url = item.get("URL")
    return ResolvedPaper(
        title=title,
        authors=", ".join(author_names) if author_names else None,
        venue=venue,
        year=year,
        doi=doi,
        official_url=official_url,
    )


def _crossref_work_by_doi(doi: str, *, timeout_seconds: int, proxy: str | None) -> ResolvedPaper:
    proxies = {"http": proxy, "https": proxy} if proxy else None
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    r = requests.get(url, timeout=timeout_seconds, proxies=proxies, headers=_crossref_headers())
    r.raise_for_status()
    item = (r.json() or {}).get("message") or {}
    return _extract_crossref_metadata(item)


def _looks_like_strict_match(reference: str, candidate: ResolvedPaper, reference_year: int | None) -> bool:
    title = _norm_text(candidate.title)
    ref = _norm_text(reference)
    if not title or not ref:
        return False

    if title not in ref:
        return False

    if reference_year is not None and candidate.year is not None and candidate.year != reference_year:
        return False

    if candidate.authors:
        first_author_token = _norm_text(candidate.authors.split(",")[0]).split(" ")
        first_author_token = [t for t in first_author_token if t]
        if first_author_token and first_author_token[-1] not in ref:
            return False

    return True


def _crossref_search(reference: str, *, timeout_seconds: int, proxy: str | None) -> ResolvedPaper:
    proxies = {"http": proxy, "https": proxy} if proxy else None
    r = requests.get(
        "https://api.crossref.org/works",
        params={"query.bibliographic": reference, "rows": 10},
        timeout=timeout_seconds,
        proxies=proxies,
        headers=_crossref_headers(),
    )
    r.raise_for_status()
    items = ((r.json() or {}).get("message") or {}).get("items") or []
    ref_year = _extract_year(reference)
    for item in items:
        candidate = _extract_crossref_metadata(item)
        if _looks_like_strict_match(reference, candidate, ref_year):
            return candidate
    return ResolvedPaper()


def _openalex_oa_by_doi(doi: str, *, timeout_seconds: int, proxy: str | None) -> tuple[str | None, str | None]:
    proxies = {"http": proxy, "https": proxy} if proxy else None
    url = f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='')}"
    r = requests.get(url, timeout=timeout_seconds, proxies=proxies)
    if r.status_code >= 400:
        return None, None
    work = r.json() or {}
    open_access = work.get("open_access") or {}
    best_oa = work.get("best_oa_location") or {}
    primary_location = work.get("primary_location") or {}
    pdf_url = (
        best_oa.get("pdf_url")
        or primary_location.get("pdf_url")
        or open_access.get("oa_url")
    )
    official_url = (
        best_oa.get("landing_page_url")
        or primary_location.get("landing_page_url")
    )
    return pdf_url, official_url


def resolve_paper(reference: str, *, timeout_seconds: int = 30, proxy: str | None = None) -> ResolvedPaper:
    doi = _norm_doi(extract_doi(reference))
    resolved = ResolvedPaper(doi=doi)

    try:
        if doi:
            resolved = _crossref_work_by_doi(doi, timeout_seconds=timeout_seconds, proxy=proxy)
        else:
            resolved = _crossref_search(reference, timeout_seconds=timeout_seconds, proxy=proxy)
    except Exception:
        # Keep best-effort behavior.
        pass

    if not resolved.doi:
        resolved.doi = doi

    if resolved.doi:
        try:
            pdf_url, landing_url = _openalex_oa_by_doi(resolved.doi, timeout_seconds=timeout_seconds, proxy=proxy)
            resolved.pdf_url = pdf_url or resolved.pdf_url
            resolved.official_url = resolved.official_url or landing_url
        except Exception:
            pass

    return resolved
