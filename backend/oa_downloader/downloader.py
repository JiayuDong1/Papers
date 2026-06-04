from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import requests


@dataclass
class DownloadResult:
    ok: bool
    path: Path | None = None
    error: str | None = None


def _is_pdf_bytes(head: bytes) -> bool:
    return head.startswith(b"%PDF")


def download_pdf(url: str, out_path: Path, *, timeout_seconds: int, retries: int, delay_seconds: float, proxy: str | None) -> DownloadResult:
    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    last_err = None
    for attempt in range(1, retries + 1):
        if attempt > 1:
            time.sleep(delay_seconds)
        try:
            with requests.get(url, stream=True, timeout=timeout_seconds, proxies=proxies, allow_redirects=True) as r:
                r.raise_for_status()

                ctype = (r.headers.get('Content-Type') or '').lower()
                if "pdf" not in ctype:
                    return DownloadResult(False, error=f"Not a PDF content-type (Content-Type={ctype or 'missing'})")

                out_path.parent.mkdir(parents=True, exist_ok=True)
                # Read first chunk for validation
                it = r.iter_content(chunk_size=8192)
                first = next(it, b"")
                if not first:
                    return DownloadResult(False, error="Empty response body")
                if not _is_pdf_bytes(first):
                    return DownloadResult(False, error=f"PDF header validation failed (Content-Type={ctype})")

                with open(out_path, 'wb') as f:
                    f.write(first)
                    for chunk in it:
                        if chunk:
                            f.write(chunk)

            return DownloadResult(True, path=out_path)
        except Exception as e:
            last_err = str(e)

    return DownloadResult(False, error=last_err or "Download failed")
