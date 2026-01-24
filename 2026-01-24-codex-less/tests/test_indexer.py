from pathlib import Path
import re

from less import cli
from less import indexer


def test_list_pdfs_finds_case_insensitive_pdfs(tmp_path):
    (tmp_path / "notes.txt").write_text("nope")
    (tmp_path / "report.pdf").write_text("pdf")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "scan.PDF").write_text("pdf")

    pdfs = indexer.list_pdfs(tmp_path)

    assert [path.name for path in pdfs] == ["report.pdf", "scan.PDF"]


def test_cli_index_passes_pdfs_to_indexer(tmp_path, capsys, monkeypatch):
    (tmp_path / "notes.txt").write_text("nope")
    (tmp_path / "report.pdf").write_text("pdf")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "scan.PDF").write_text("pdf")

    captured_paths = []

    def fake_index_pdfs(paths):
        captured_paths.extend(paths)

    monkeypatch.setattr(indexer, "index_pdfs", fake_index_pdfs)

    exit_code = cli.main(["index", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert [path.name for path in captured_paths] == ["report.pdf", "scan.PDF"]
    assert "Found 2 PDF files." in captured.out


def test_extract_text_from_pdf():
    pdf_path = Path(__file__).parent / "ai-companies.pdf"

    text = indexer.extract_text(pdf_path)

    assert "Top Generative AI Solution Providers" in text
    assert "OpenAI" in text
    assert "immediate productivity" in text
    assert "long-context" in text


def test_chunk_text_keeps_sentence_boundaries():
    sentence = "A" * 260 + "."
    text = " ".join([sentence, sentence, sentence, sentence])

    chunks = indexer.chunk_text(
        text,
        max_chars=2000,
        min_chars=500,
        nlp=_fake_nlp(),
    )

    assert chunks == [f"{sentence} {sentence}", f"{sentence} {sentence}"]


def test_chunk_text_respects_max_when_sentence_exceeds():
    long_sentence = "B" * 2100 + "."
    text = f"{long_sentence} Short sentence."

    chunks = indexer.chunk_text(
        text,
        max_chars=2000,
        min_chars=500,
        nlp=_fake_nlp(),
    )

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
