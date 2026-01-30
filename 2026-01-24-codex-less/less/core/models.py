from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class SearchResult:
    text: str
    metadata: dict[str, object]
    score: float
