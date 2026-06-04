from __future__ import annotations

from pathlib import Path

from .config import Config, ensure_dir
from .input_readers import read_docx_refs, read_xlsx_refs
from .layout import derive_run_dir
from .parse import split_references, normalize_text
from .resolver import resolve_paper
from .results import write_results, load_previous_results


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

    rows: list[dict] = []
    for i, ref in enumerate(refs, start=1):
        print(f"[{i}/{len(refs)}] Resolving...")
        resolved = resolve_paper(ref)

        doi_key = (resolved.doi or "").strip().lower()
        if doi_key and doi_key in prev_success:
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

        # TODO: implement download + naming + OA
        status = "unresolved"
        err = None
        out_pdf = None

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

    write_results(results_path, rows)
    print(f"Wrote results: {results_path}")
