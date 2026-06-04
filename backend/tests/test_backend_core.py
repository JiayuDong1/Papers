import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from oa_downloader.downloader import download_pdf
from oa_downloader.layout import derive_run_dir
from oa_downloader.resolver import _norm_doi


class _FakeResponse:
    def __init__(self, *, content_type: str, chunks: list[bytes], status_code: int = 200):
        self.headers = {"Content-Type": content_type}
        self._chunks = chunks
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def iter_content(self, chunk_size=8192):
        del chunk_size
        for chunk in self._chunks:
            yield chunk

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        return False


class BackendCoreTests(unittest.TestCase):
    def test_derive_run_dir_sanitizes_input_name(self):
        run_dir = derive_run_dir(Path(r"D:\Papers"), "/tmp/a:b?.docx")
        self.assertEqual(run_dir.as_posix(), "D:\\Papers/a_b_")

    def test_norm_doi_handles_url_form(self):
        self.assertEqual(_norm_doi("https://doi.org/10.1000/ABC-12"), "10.1000/abc-12")

    @patch("oa_downloader.downloader.requests.get")
    def test_download_pdf_rejects_non_pdf_content_type(self, mock_get):
        mock_get.return_value = _FakeResponse(
            content_type="text/html",
            chunks=[b"%PDF-1.7 fake"],
        )
        with tempfile.TemporaryDirectory() as td:
            result = download_pdf(
                "https://example.com/paper",
                Path(td) / "paper.pdf",
                timeout_seconds=5,
                retries=1,
                delay_seconds=0,
                proxy=None,
            )
        self.assertFalse(result.ok)
        self.assertIn("content-type", (result.error or "").lower())


if __name__ == "__main__":
    unittest.main()
