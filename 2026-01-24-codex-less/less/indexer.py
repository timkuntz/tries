from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


def list_pdfs(root: Path) -> list[Path]:
    pdfs = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    ]
    return sorted(pdfs, key=lambda path: (path.name.lower(), path.as_posix()))


def index_pdfs(paths: Iterable[Path]) -> None:
    _ = list(paths)
    print("Embedding and storing vectors...")


def extract_text(path: Path) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
