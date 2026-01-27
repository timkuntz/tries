from pathlib import Path

from less.core.models import Chunk
from less.core.use_cases import IndexDirectoryUseCase, IndexPdfUseCase, build_chunks_from_pages


def test_build_chunks_from_pages_includes_pdf_metadata():
    pdf_path = Path(__file__).parents[1] / "ai-companies.pdf"
    chunker = _FakeChunker()

    chunks = build_chunks_from_pages(
        ["First page text."],
        pdf_path,
        chunker,
        min_chars=1,
        max_chars=2000,
    )

    assert len(chunks) == 1
    assert chunks[0].metadata["pdf_name"] == pdf_path.name
    assert chunks[0].metadata["pdf_path"] == str(pdf_path)
    assert chunks[0].metadata["page_number"] == 1


def test_index_pdf_use_case_stores_embeddings():
    pdf_path = Path(__file__).parents[1] / "ai-companies.pdf"
    extractor = _FakeExtractor(pages=["Sentence one.", "Sentence two."])
    chunker = _FakeChunker()
    embedder = _FakeEmbedder()
    store = _FakeVectorStore()

    use_case = IndexPdfUseCase(
        extractor,
        chunker,
        embedder,
        store,
        min_chars=1,
        max_chars=2000,
    )

    chunks = use_case.index_pdf(pdf_path)

    assert len(chunks) == 2
    assert store.added_chunks == chunks
    assert store.added_embeddings == [[1.0, 0.0], [1.0, 0.0]]


def test_index_directory_counts_chunks():
    pdf_path = Path(__file__).parents[1] / "ai-companies.pdf"
    extractor = _FakeExtractor(pages=["One.", "Two."])
    chunker = _FakeChunker()
    embedder = _FakeEmbedder()
    store = _FakeVectorStore()
    pdf_use_case = IndexPdfUseCase(
        extractor,
        chunker,
        embedder,
        store,
        min_chars=1,
        max_chars=2000,
    )

    dir_use_case = IndexDirectoryUseCase(pdf_use_case)

    count = dir_use_case.index_paths([pdf_path])

    assert count == 2


class _FakeExtractor:
    def __init__(self, pages: list[str]) -> None:
        self._pages = pages

    def extract_pages(self, _path: Path) -> list[str]:
        return list(self._pages)


class _FakeChunker:
    def chunk_text(self, text: str, *, min_chars: int, max_chars: int) -> list[str]:
        _ = min_chars
        _ = max_chars
        return [text]


class _FakeEmbedder:
    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class _FakeVectorStore:
    def __init__(self) -> None:
        self.added_chunks: list[Chunk] = []
        self.added_embeddings: list[list[float]] = []

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.added_chunks = list(chunks)
        self.added_embeddings = list(embeddings)
