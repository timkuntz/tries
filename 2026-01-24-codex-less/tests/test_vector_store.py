from pathlib import Path

from less import vector_store


def test_index_pdf_stores_chunks_in_vector_db():
    pdf_path = Path(__file__).parent / "ai-companies.pdf"
    collection = _FakeCollection()
    embedder = _FakeEmbedder()

    chunks = vector_store.index_pdf_to_collection(
        pdf_path,
        collection,
        embedder,
        min_chars=500,
        max_chars=2000,
        nlp=_fake_nlp(),
    )

    stored = collection.get(include=["documents", "metadatas"])

    assert len(chunks) > 0
    assert collection.count() == len(chunks)
    assert any("OpenAI" in doc for doc in stored["documents"])
    assert all(meta["source_path"] == str(pdf_path) for meta in stored["metadatas"])
    assert all("page_number" in meta for meta in stored["metadatas"])


def _fake_nlp():
    class _Sent:
        def __init__(self, text: str) -> None:
            self.text = text

    class _Doc:
        def __init__(self, sents) -> None:
            self.sents = sents

    class _NLP:
        def __call__(self, text: str) -> _Doc:
            sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
            return _Doc([_Sent(f"{sentence}.") for sentence in sentences])

    return _NLP()


class _FakeEmbedder:
    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 0.0] for text in texts]


class _FakeCollection:
    def __init__(self) -> None:
        self._documents: list[str] = []
        self._metadatas: list[dict[str, object]] = []
        self._ids: list[str] = []

    def add(self, *, ids, documents, metadatas, embeddings) -> None:
        _ = embeddings
        self._ids.extend(ids)
        self._documents.extend(documents)
        self._metadatas.extend(metadatas)

    def count(self) -> int:
        return len(self._ids)

    def get(self, *, include):
        result = {}
        if "documents" in include:
            result["documents"] = list(self._documents)
        if "metadatas" in include:
            result["metadatas"] = list(self._metadatas)
        return result
