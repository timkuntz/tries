from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import Chunk


class PdfTextExtractor(Protocol):
    def extract_pages(self, path: Path) -> list[str]:
        raise NotImplementedError


class SentenceChunker(Protocol):
    def chunk_text(self, text: str, *, min_chars: int, max_chars: int) -> list[str]:
        raise NotImplementedError


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class VectorStore(Protocol):
    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        raise NotImplementedError
