from less.core.models import SearchResult
from less.core.use_cases import SearchUseCase


def test_search_use_case_embeds_and_queries():
    embedder = _FakeEmbedder()
    store = _FakeStore()
    use_case = SearchUseCase(embedder, store, top_k=2)

    results = use_case.search("hello world")

    assert embedder.encoded == [["hello world"]]
    assert store.queries == [([0.5, 0.1], 2)]
    assert results == [SearchResult(text="hit", metadata={"a": 1}, score=0.2)]


class _FakeEmbedder:
    def __init__(self) -> None:
        self.encoded = []

    def encode(self, texts: list[str]) -> list[list[float]]:
        self.encoded.append(texts)
        return [[0.5, 0.1] for _ in texts]


class _FakeStore:
    def __init__(self) -> None:
        self.queries = []

    def query(self, embedding, *, top_k: int):
        self.queries.append((embedding, top_k))
        return [SearchResult(text="hit", metadata={"a": 1}, score=0.2)]
