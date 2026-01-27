from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Protocol

from pypdf import PdfReader

if TYPE_CHECKING:
    from spacy.language import Language

class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


def list_pdfs(root: Path) -> list[Path]:
    pdfs = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    ]
    return sorted(pdfs, key=lambda path: (path.name.lower(), path.as_posix()))


def index_pdfs(
    paths: Iterable[Path],
    *,
    collection_name: str = "less",
    persist_path: Path | None = Path(".less/chroma"),
    embedder: Embedder | None = None,
    nlp: "Language | None" = None,
    max_chars: int = 2000,
    min_chars: int = 500,
) -> int:
    from . import vector_store

    pdfs = list(paths)
    if embedder is None:
        print("Using SentenceTransformerEmbedder")
        embedder = SentenceTransformerEmbedder()

    collection = vector_store.get_collection(
        collection_name,
        persist_path=persist_path,
    )

    stored = 0
    for pdf in pdfs:
        chunks = vector_store.index_pdf_to_collection(
            pdf,
            collection,
            embedder,
            max_chars=max_chars,
            min_chars=min_chars,
            nlp=nlp,
        )
        stored += len(chunks)

    print(f"Embedding and storing {stored} chunks...")
    return stored


def extract_text(path: Path) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_pages(path: Path) -> list[str]:
    reader = PdfReader(path)
    return [page.extract_text() or "" for page in reader.pages]


def _load_spacy():
    try:
        import spacy as spacy_module
    except Exception as exc:  # pragma: no cover - import-time failure handling
        raise RuntimeError("spaCy is required for sentence chunking.") from exc
    return spacy_module


def build_nlp() -> "Language":
    spacy_module = _load_spacy()
    nlp = spacy_module.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


def chunk_text(
    text: str,
    max_chars: int = 2000,
    min_chars: int = 500,
    nlp: "Language | None" = None,
) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive.")
    if min_chars <= 0:
        raise ValueError("min_chars must be positive.")
    if min_chars > max_chars:
        raise ValueError("min_chars must be <= max_chars.")

    if nlp is None:
        nlp = build_nlp()

    sentences = [sent.text.strip() for sent in nlp(text).sents if sent.text.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if not current:
            if sentence_len > max_chars:
                chunks.append(sentence)
                continue
            current = [sentence]
            current_len = sentence_len
            continue

        separator_len = 1
        if current_len + separator_len + sentence_len > max_chars:
            chunks.append(" ".join(current))
            if sentence_len > max_chars:
                chunks.append(sentence)
                current = []
                current_len = 0
                continue
            current = [sentence]
            current_len = sentence_len
        else:
            current.append(sentence)
            current_len += separator_len + sentence_len

        if current_len >= min_chars:
            chunks.append(" ".join(current))
            current = []
            current_len = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = self._load_model(model_name)

    @staticmethod
    def _load_model(model_name: str):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
