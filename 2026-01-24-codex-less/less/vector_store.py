from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from . import indexer
from .indexer import Embedder

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection
    from spacy.language import Language


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, object]


def _load_chromadb():
    try:
        import chromadb as chromadb_module
    except Exception as exc:  # pragma: no cover - import-time failure handling
        message = (
            "chromadb is required for vector storage. "
            "Install compatible dependencies, e.g. "
            "`pip install chromadb pydantic-settings`."
        )
        raise RuntimeError(message) from exc
    return chromadb_module


def get_collection(
    name: str,
    *,
    persist_path: Path | None = None,
    collection: "Collection | None" = None,
):
    chromadb_module = _load_chromadb()
    if collection is None:
        settings = chromadb_module.config.Settings(
            is_persistent=persist_path is not None,
        )
        if persist_path is None:
            chroma_client = chromadb_module.Client(settings)
        else:
            persist_path.mkdir(parents=True, exist_ok=True)
            chroma_client = chromadb_module.PersistentClient(
                path=str(persist_path),
                settings=settings,
            )
        return chroma_client.get_or_create_collection(name)
    return collection


def build_chunks_from_pages(
    pages: Iterable[str],
    source_path: Path,
    *,
    max_chars: int = 2000,
    min_chars: int = 500,
    nlp: "Language | None" = None,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):
        page_chunks = indexer.chunk_text(
            page_text,
            max_chars=max_chars,
            min_chars=min_chars,
            nlp=nlp,
        )
        for chunk in page_chunks:
            chunk_id = f"{source_path}::p{page_number}::c{chunk_index}"
            metadata = {
                "source_path": str(source_path),
                "page_number": page_number,
                "chunk_index": chunk_index,
            }
            chunks.append(Chunk(chunk_id=chunk_id, text=chunk, metadata=metadata))
            chunk_index += 1

    return chunks


def store_chunks(
    collection: "Collection",
    chunks: Iterable[Chunk],
    embedder: Embedder,
) -> None:
    chunk_list = list(chunks)
    if not chunk_list:
        return
    texts = [chunk.text for chunk in chunk_list]
    embeddings = embedder.encode(texts)
    collection.add(
        ids=[chunk.chunk_id for chunk in chunk_list],
        documents=texts,
        metadatas=[chunk.metadata for chunk in chunk_list],
        embeddings=embeddings,
    )


def index_pdf_to_collection(
    path: Path,
    collection: "Collection",
    embedder: Embedder,
    *,
    max_chars: int = 2000,
    min_chars: int = 500,
    nlp: "Language | None" = None,
) -> list[Chunk]:
    pages = indexer.extract_pages(path)
    chunks = build_chunks_from_pages(
        pages,
        path,
        max_chars=max_chars,
        min_chars=min_chars,
        nlp=nlp,
    )
    store_chunks(collection, chunks, embedder)
    return chunks
