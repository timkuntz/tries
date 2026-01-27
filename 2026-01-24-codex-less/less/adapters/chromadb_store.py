from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..core.models import Chunk
from ..core.ports import VectorStore

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


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


class ChromaVectorStore(VectorStore):
    def __init__(self, collection: "Collection") -> None:
        self._collection = collection

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=embeddings,
        )
