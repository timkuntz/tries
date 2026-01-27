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


def test_cli_index_command_uses_use_case(tmp_path, monkeypatch, capsys):
    captured = {}

    def fake_list_pdfs(_root):
        return [tmp_path / "sample.pdf"]

    class _FakeUseCase:
        def index_paths(self, paths):
            captured["paths"] = list(paths)
            return 3

    monkeypatch.setattr(cli.filesystem, "list_pdfs", fake_list_pdfs)
    monkeypatch.setattr(cli, "build_index_use_case", lambda: _FakeUseCase())

    exit_code = cli.main(["index", str(tmp_path)])
    output = capsys.readouterr()

    assert exit_code == 0
    assert "Found 1 PDF files." in output.out
    assert "Embedding and storing 3 chunks..." in output.out
    assert captured["paths"] == [tmp_path / "sample.pdf"]
