import re

from less.adapters.spacy_chunker import SpacySentenceChunker


def test_spacy_chunker_respects_min_and_sentence_boundaries():
    sentence = "A" * 260 + "."
    text = " ".join([sentence, sentence, sentence, sentence])

    chunker = SpacySentenceChunker(min_chars=500, max_chars=2000, nlp=_fake_nlp())
    chunks = chunker.chunk_text(text, min_chars=500, max_chars=2000)

    assert chunks == [f"{sentence} {sentence}", f"{sentence} {sentence}"]


def test_spacy_chunker_allows_long_sentence_over_max():
    long_sentence = "B" * 2100 + "."
    text = f"{long_sentence} Short sentence."

    chunker = SpacySentenceChunker(min_chars=500, max_chars=2000, nlp=_fake_nlp())
    chunks = chunker.chunk_text(text, min_chars=500, max_chars=2000)

    assert chunks[0] == long_sentence
    assert chunks[1] == "Short sentence."


def _fake_nlp():
    class _Sent:
        def __init__(self, text: str) -> None:
            self.text = text

    class _Doc:
        def __init__(self, sents) -> None:
            self.sents = sents

    class _NLP:
        def __call__(self, text: str) -> _Doc:
            matches = re.findall(r"[^.!?]+[.!?]", text)
            sentences = [match.strip() for match in matches]
            return _Doc([_Sent(sentence) for sentence in sentences])

    return _NLP()
