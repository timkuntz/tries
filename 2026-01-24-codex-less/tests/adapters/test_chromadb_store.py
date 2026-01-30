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


def test_chroma_vector_store_queries_results():
    collection = _FakeCollection()
    collection.query_result = {
        "documents": [["Doc"]],
        "metadatas": [[{"pdf_name": "sample.pdf", "page_number": 1}]],
        "distances": [[0.42]],
    }

    store = ChromaVectorStore(collection)
    results = store.query([0.1, 0.2], top_k=3)

    assert collection.query_args == {
        "query_embeddings": [[0.1, 0.2]],
        "n_results": 3,
        "include": ["documents", "metadatas", "distances"],
    }
    assert results[0].text == "Doc"
    assert results[0].metadata["pdf_name"] == "sample.pdf"
    assert results[0].score == 0.42


class _FakeCollection:
    def __init__(self) -> None:
        self.ids = []
        self.documents = []
        self.metadatas = []
        self.embeddings = []
        self.query_result = {}
        self.query_args = {}

    def add(self, *, ids, documents, metadatas, embeddings) -> None:
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.embeddings.extend(embeddings)

    def query(self, **kwargs):
        self.query_args = kwargs
        return self.query_result
