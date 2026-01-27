from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from ..core.ports import PdfTextExtractor


class PypdfExtractor(PdfTextExtractor):
    def extract_pages(self, path: Path) -> list[str]:
        reader = PdfReader(path)
        return [page.extract_text() or "" for page in reader.pages]
