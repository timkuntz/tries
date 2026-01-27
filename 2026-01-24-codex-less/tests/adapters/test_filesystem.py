from pathlib import Path

from less.adapters import filesystem


def test_list_pdfs_finds_pdfs_case_insensitive(tmp_path):
    (tmp_path / "notes.txt").write_text("nope")
    (tmp_path / "report.pdf").write_text("pdf")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "scan.PDF").write_text("pdf")

    pdfs = filesystem.list_pdfs(tmp_path)

    assert [path.name for path in pdfs] == ["report.pdf", "scan.PDF"]
