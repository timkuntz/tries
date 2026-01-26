import pytest

from less import cli


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["search", "demo query"], "Searching for: demo query"),
    ],
)
def test_cli_commands(args, expected, capsys):
    exit_code = cli.main(args)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert expected in captured.out


def test_cli_index_command_uses_indexer(tmp_path, monkeypatch, capsys):
    captured_paths = {}

    def fake_index_pdfs(paths, **_kwargs):
        captured_paths["paths"] = list(paths)
        return 0

    monkeypatch.setattr(cli.indexer, "index_pdfs", fake_index_pdfs)

    exit_code = cli.main(["index", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Found 0 PDF files." in captured.out
    assert captured_paths["paths"] == []
