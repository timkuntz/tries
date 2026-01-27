from pathlib import Path

from less.adapters.chromadb_store import ChromaVectorStore
from less.core.models import Chunk


def test_chroma_vector_store_adds_chunks():
    pdf_path = Path(__file__).parents[1] / "ai-companies.pdf"
    chunks = [
        Chunk(
            chunk_id="chunk-1",
            text="Hello world.",
            metadata={
                "pdf_name": pdf_path.name,
                "pdf_path": str(pdf_path),
                "page_number": 1,
                "chunk_index": 0,
            },
        ),
    ]
    embeddings = [[0.1, 0.2]]
    collection = _FakeCollection()

    store = ChromaVectorStore(collection)
    store.add_chunks(chunks, embeddings)

    assert collection.ids == ["chunk-1"]
    assert collection.documents == ["Hello world."]
    assert collection.metadatas[0]["pdf_name"] == pdf_path.name


class _FakeCollection:
    def __init__(self) -> None:
        self.ids = []
        self.documents = []
        self.metadatas = []
        self.embeddings = []

    def add(self, *, ids, documents, metadatas, embeddings) -> None:
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.embeddings.extend(embeddings)
