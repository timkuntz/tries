from pathlib import Path

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
