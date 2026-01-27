from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.ports import SentenceChunker

if TYPE_CHECKING:
    from spacy.language import Language


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


class SpacySentenceChunker(SentenceChunker):
    def __init__(
        self,
        *,
        min_chars: int = 500,
        max_chars: int = 2000,
        nlp: "Language | None" = None,
    ) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars must be positive.")
        if min_chars <= 0:
            raise ValueError("min_chars must be positive.")
        if min_chars > max_chars:
            raise ValueError("min_chars must be <= max_chars.")

        self._min_chars = min_chars
        self._max_chars = max_chars
        self._nlp = nlp

    def chunk_text(self, text: str, *, min_chars: int, max_chars: int) -> list[str]:
        if self._nlp is None:
            self._nlp = build_nlp()

        if max_chars <= 0:
            raise ValueError("max_chars must be positive.")
        if min_chars <= 0:
            raise ValueError("min_chars must be positive.")
        if min_chars > max_chars:
            raise ValueError("min_chars must be <= max_chars.")

        sentences = [sent.text.strip() for sent in self._nlp(text).sents if sent.text.strip()]
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
