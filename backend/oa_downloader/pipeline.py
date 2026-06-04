from __future__ import annotations

from pathlib import Path

from .config import Config, ensure_dir, sanitize_folder_name
from .downloader import download_pdf
from .input_readers import read_docx_refs, read_xlsx_refs
from .layout import derive_run_dir
from .parse import split_references, normalize_text
from .resolver import resolve_paper
from .results import write_results, load_previous_results

MAX_FILENAME_STEM_LENGTH = 120


def run_pipeline(
    *,
    input_file: str | None,
    pasted_text: str | None,
    output_root: str,
    delay_seconds: float,
    retries: int,
    timeout_seconds: int,
    proxy: str | None,
    resume: bool,
) -> None:
    cfg = Config(
        output_root=Path(output_root),
        delay_seconds=delay_seconds,
        retries=retries,
        timeout_seconds=timeout_seconds,
        proxy=proxy,
        resume=resume,
    )

    run_dir = derive_run_dir(cfg.output_root, input_file)
    ensure_dir(run_dir)
    results_path = run_dir / "results.xlsx"

    prev = load_previous_results(results_path) if cfg.resume else None
    prev_success = set()
    if prev is not None and "doi" in prev.columns and "status" in prev.columns:
        for _, row in prev.iterrows():
            if str(row.get("status") or "").lower() == "downloaded":
                doi = str(row.get("doi") or "").strip().lower()
                if doi:
                    prev_success.add(doi)

    refs: list[str] = []
    if input_file:
        if input_file.lower().endswith('.docx'):
            refs = read_docx_refs(input_file)
        elif input_file.lower().endswith('.xlsx'):
            refs = read_xlsx_refs(input_file)
        else:
            raise ValueError("Unsupported input file type")
    else:
        refs = [normalize_text(x) for x in split_references(pasted_text or "")]

    print(f"Run dir: {run_dir}")
    print(f"References: {len(refs)}")
    pdf_dir = run_dir / "pdfs"
    ensure_dir(pdf_dir)

    rows: list[dict] = []
    seen_doi: set[str] = set()
    for i, ref in enumerate(refs, start=1):
        print(f"PROGRESS {i}/{len(refs)}")
        print(f"[{i}/{len(refs)}] Resolving...")
        resolved = resolve_paper(ref, timeout_seconds=cfg.timeout_seconds, proxy=cfg.proxy)

        doi_key = (resolved.doi or "").strip().lower()
        if doi_key and doi_key in prev_success:
            print(f"[{i}/{len(refs)}] Skip (resume): {resolved.doi}")
            rows.append({
                "input_reference": ref,
                "title": resolved.title,
                "authors": resolved.authors,
                "venue": resolved.venue,
                "year": resolved.year,
                "doi": resolved.doi,
                "pdf_url": resolved.pdf_url,
                "official_url": resolved.official_url,
                "status": "skipped(resume)",
                "error": None,
                "output_pdf_path": None,
            })
            continue
        if doi_key and doi_key in seen_doi:
            print(f"[{i}/{len(refs)}] Skip (duplicate DOI): {resolved.doi}")
            rows.append({
                "input_reference": ref,
                "title": resolved.title,
                "authors": resolved.authors,
                "venue": resolved.venue,
                "year": resolved.year,
                "doi": resolved.doi,
                "pdf_url": resolved.pdf_url,
                "official_url": resolved.official_url,
                "status": "duplicate(skipped)",
                "error": None,
                "output_pdf_path": None,
            })
            continue

        status = "unresolved"
        err = None
        out_pdf = None
        if resolved.pdf_url:
            pdf_base = resolved.doi or resolved.title or f"paper_{i}"
            pdf_name = sanitize_folder_name(pdf_base)[:MAX_FILENAME_STEM_LENGTH] + ".pdf"
            out_pdf = pdf_dir / pdf_name
            print(f"[{i}/{len(refs)}] Downloading PDF...")
            result = download_pdf(
                resolved.pdf_url,
                out_pdf,
                timeout_seconds=cfg.timeout_seconds,
                retries=cfg.retries,
                delay_seconds=cfg.delay_seconds,
                proxy=cfg.proxy,
            )
            if result.ok:
                status = "downloaded"
                print(f"[{i}/{len(refs)}] Downloaded: {result.path}")
            else:
                status = "download_failed"
                err = result.error
                out_pdf = None
                print(f"[{i}/{len(refs)}] Download failed: {err}")
        elif resolved.doi or resolved.title:
            status = "resolved_no_oa_pdf"
            print(f"[{i}/{len(refs)}] No OA PDF URL found")

        rows.append({
            "input_reference": ref,
            "title": resolved.title,
            "authors": resolved.authors,
            "venue": resolved.venue,
            "year": resolved.year,
            "doi": resolved.doi,
            "pdf_url": resolved.pdf_url,
            "official_url": resolved.official_url,
            "status": status,
            "error": err,
            "output_pdf_path": str(out_pdf) if out_pdf else None,
        })
        if doi_key:
            seen_doi.add(doi_key)

    write_results(results_path, rows)
    print(f"Wrote results: {results_path}")
