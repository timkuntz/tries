from __future__ import annotations

from pathlib import Path

from .models import Chunk, SearchResult
from .ports import Embedder, PdfTextExtractor, SentenceChunker, VectorStore


def build_chunks_from_pages(
    pages: list[str],
    source_path: Path,
    chunker: SentenceChunker,
    *,
    min_chars: int,
    max_chars: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):
        page_chunks = chunker.chunk_text(
            page_text,
            min_chars=min_chars,
            max_chars=max_chars,
        )
        for chunk in page_chunks:
            chunk_id = f"{source_path}::p{page_number}::c{chunk_index}"
            metadata = {
                "pdf_name": source_path.name,
                "pdf_path": str(source_path),
                "page_number": page_number,
                "chunk_index": chunk_index,
            }
            chunks.append(Chunk(chunk_id=chunk_id, text=chunk, metadata=metadata))
            chunk_index += 1

    return chunks


class IndexPdfUseCase:
    def __init__(
        self,
        extractor: PdfTextExtractor,
        chunker: SentenceChunker,
        embedder: Embedder,
        vector_store: VectorStore,
        *,
        min_chars: int = 500,
        max_chars: int = 2000,
    ) -> None:
        if min_chars <= 0:
            raise ValueError("min_chars must be positive.")
        if max_chars <= 0:
            raise ValueError("max_chars must be positive.")
        if min_chars > max_chars:
            raise ValueError("min_chars must be <= max_chars.")

        self._extractor = extractor
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store
        self._min_chars = min_chars
        self._max_chars = max_chars

    def index_pdf(self, path: Path) -> list[Chunk]:
        pages = self._extractor.extract_pages(path)
        chunks = build_chunks_from_pages(
            pages,
            path,
            self._chunker,
            min_chars=self._min_chars,
            max_chars=self._max_chars,
        )
        if not chunks:
            return []
        embeddings = self._embedder.encode([chunk.text for chunk in chunks])
        self._vector_store.add_chunks(chunks, embeddings)
        return chunks


class IndexDirectoryUseCase:
    def __init__(self, pdf_use_case: IndexPdfUseCase) -> None:
        self._pdf_use_case = pdf_use_case

    def index_paths(self, paths: list[Path]) -> int:
        total = 0
        for path in paths:
            total += len(self._pdf_use_case.index_pdf(path))
        return total


class SearchUseCase:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        *,
        top_k: int = 5,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")
        self._embedder = embedder
        self._vector_store = vector_store
        self._top_k = top_k

    def search(self, query: str) -> list[SearchResult]:
        embeddings = self._embedder.encode([query])
        return self._vector_store.query(embeddings[0], top_k=self._top_k)
